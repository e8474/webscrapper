import requests
from bs4 import BeautifulSoup
from time import sleep
import xlrd

links = set()

def url_to_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup

def find_all_tr(soup):
    data = soup.find_all('tr')
    return data

def find_all_td(soup):
    data = soup.find_all('td')
    return data

def search_links(soup, count, base):
    if(count == 0 or len(links)>500):
        return
    for a in soup.find_all('a', href=True):
        if(a['href'].find(base) == -1):
            continue
        links.add(a['href'])
        print(a['href'])
        try:
            search_links(url_to_soup(a['href']), count-1, base)
        except:
            continue
    print(len(links))
    return links

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

def readfromxl():
    loc =r'C:\Users\ericlee2\Downloads\lotlist.xls'
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    lotnames = []
    for i in range(sheet.nrows):
        lotnames.append(sheet.cell_value(i, 0))
    del lotnames[:2]
    print(lotnames)

def get_permits():
    link = 'https://transport.tamu.edu/Parking/faqpermit/info.aspx'
    soup = url_to_soup(link)
    table = soup.find(lambda  tag: tag.name=='table')
    rows = table.findAll(lambda  tag: tag.name == 'tr')
    print(rows)

if __name__ == '__main__':
    garagedata = get_garage_rates()
    #print(garagedata)
    #readfromxl()
    print(get_permits())
