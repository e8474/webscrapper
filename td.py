#This .py had many functions for our various approaches to our project
#The main purpose of this file was to prepare the base excel sheet that we eventually manually input data into

import requests
from bs4 import BeautifulSoup
import xlrd
from xlwt import Workbook

#holds links from webcrawl
links = set()

#takes url string and converts it to soup objeect using html5lib interpreter
def url_to_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup

#returns list of all instances of tr in a soup
def find_all_tr(soup):
    data = soup.find_all('tr')
    return data

#returns list of all instances of td in a soup
def find_all_td(soup):
    data = soup.find_all('td')
    return data

#does a webcrawl to find links recurively, the # of level it searches is based on count, base can be a keyword required for links to curate the final set
def search_links(soup, count, base):
    if(count == 0 or len(links)>500): #if # of links is greater than 500 or reached end of recursion (base case)
        return
    #print(soup.find_all('a', href=True))
    for a in soup.find_all('a', href=True): #for every href in soup we try to find the base and if it exists then add it to set links
        if(a['href'].find(base) == -1):
            continue
        links.add(a['href'])
        try:
            search_links(url_to_soup(a['href']), count-1, base)#attempt a recursive call but if url doesn't work or smth just move to next
        except:
            continue
    return links

#gets list of lot names from parking site
def search_lots():
    link = 'https://transport.tamu.edu/Parking/faqpermit/info-offcampus.aspx'
    soup = url_to_soup(link)
    table = soup.find(class_='card-deck')
    rows = table.findAll('a')
    names = set()
    for p in rows:
            names.add(p.text)
    return (names)

#gets paid parking rates from parking site
def get_garage_rates():
    link = 'https://transport.tamu.edu/Parking/visitor.aspx'
    soup = url_to_soup(link)
    sssoup = find_all_td(soup)
    souplist = [td.text for td in sssoup]
    finallist = []
    for n in souplist:
        if (n.find('\n') >= 0):
            break
        finallist.append(n)
    return finallist

#reads from a excel sheet we curated
def readfromxl():
    loc =r'C:\Users\ericlee2\Downloads\lotlist.xls'
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    lotnames = []
    goodrows = []
    for i in range(sheet.nrows-3):
        if(type(sheet.cell_value(i+2,2)) == float and sheet.cell_value(i+2,2)>0):
            lotnames.append(sheet.cell_value(i+2, 0))
            goodrows.append(i+3)
    return lotnames

#writes data into excel sheet
def writedata_xl(lotnames):
    wb = Workbook() #creates excel workbook
    sheet1 = wb.add_sheet('Sheet 1') #makes a sheet called Sheet 1
    sheet2 = wb.add_sheet('PAID PARKING') #makes a sheet called "PAID PARKING"
    #puts garage rates into 'PAID PARKING'
    garage_rate = get_garage_rates()
    ratelinecouter = 0
    shift = 0
    for item in garage_rate:
        sheet2.write(ratelinecouter,shift, item)
        shift += 1
        if(shift == 3):
            shift = 0
            ratelinecouter += 1
    #Puts lot names in excelsheet and preps other identifier columns
    linecounter = 1
    hour = 0
    ticker = 1
    sheet1.write(0, 0, 'Lot/Garage')
    sheet1.write(0, 1, 'Day')
    sheet1.write(0, 2, 'Hour')
    for name in lotnames:
        for i in range(96):
            sheet1.write(linecounter, 0, name)
            if (ticker == 3):
                sheet1.write(linecounter, 1, 'break')
            if (ticker == 4):
                sheet1.write(linecounter, 1, 'summer')
            if (ticker == 1):
                sheet1.write(linecounter, 1, 'weekday')
            if (ticker == 2):
                sheet1.write(linecounter, 1, 'weekend')
            if ((i + 1) % 24 == 0):
                ticker += 1
                if(ticker == 5):
                    ticker = 1
            if(hour == 24):
                hour = 0
            sheet1.write(linecounter, 2, hour)
            hour += 1
            linecounter += 1

    #saves all prep into an excel sheet called exmaples.xls
    wb.save('examples.xls')

#webscrapes a list of permit names from trasport website
def get_permits():
    link = 'https://transport.tamu.edu/Parking/faqpermit/info.aspx'
    soup = url_to_soup(link)
    table = soup.find(lambda  tag: tag.name=='table')
    rows = table.findAll(lambda  tag: tag.name == 'tr')
    names = []
    for tr in rows:
        td_list = tr.findAll('td')
        if(len(td_list)>0):
            names.append(td_list[0].text)
    return(names)

#natural language interpter that searches for key words referencing not avaiable parking and returns boolean
def not_avail_parking_words(sentence):
    checkwords = ['unavailable','reserved', 'restricted', 'not available', 'not permitted', 'not open']
    for word in checkwords:
        if(sentence.find(word)>=0):
            return True
    return False

#natural language interpreter that searches for key words referencing avaiable parking and return boolean
def avail_parking_words(sentence):
    checkwords = ['available', 'permitted', 'open']
    for word in checkwords:
        if(sentence.find(word)>=0):
            return True
    return False

#using the natural language interpreters to determine the availability status of a sentence
def ambiguous_sentence_determiner(sentence):
    if(not_avail_parking_words(sentence)):
        return 'not available'
    elif(avail_parking_words(sentence)):
        return 'available'
    else:
        return

#webscrapes data about event parking from parking site
def event_parking_lots():
    link = 'https://transport.tamu.edu/Parking/events/annual.aspx'
    soup = url_to_soup(link)
    cards = soup.find_all(class_ = 'card-body')
    sentences = []
    headers = soup.find_all(class_ = 'card-header pt-4"')
    for card in cards:
        words = card.find_all('p')
        #headers.append(card.find_all(class_='card-link'))
        for word in words:
            sentences.append(word.text)
    ret = []
    for header in headers:
        ret.append(header.find_all(class_ = 'card-link'))
    print(ret)
    #print(sentences)

#webscrapes site for any mention of lot or garage in the paragraph objects in a site
def search_lots_and_garage(site):
    checkwords = ['lot', 'Lot', 'Lots', 'lots', 'Garage', 'garage']
    soup = url_to_soup(site)
    texts = soup.find_all('p')
    sentences = []
    for text in texts:
        sentences.append(text.text)

    print(sentences)

if __name__ == '__main__':
    #garagedata = get_garage_rates()
    #print(garagedata)
    #readfromxl()
    #print(get_permits())
    #event_parking_lots()
    #print(len(search_lots()))
    #event_parking_lots()
    lots = []
    f = open(r'.\data.txt', 'r')
    for line in f:
        lots.append(line)
    writedata_xl(lots)