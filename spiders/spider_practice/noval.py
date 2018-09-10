from gevent import monkey
monkey.patch_all()
import requests
import lxml
from lxml import etree
import re,os
from bs4 import BeautifulSoup
from urllib import parse
from gevent.pool import Pool

#输入小说名和保存位置
searchkey = '斗破苍穹'
path = r'F:\vid'
urlpath = ''
url = ''
urls = set()


#requests设置
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
payload = {'keyword':searchkey}
requests.packages.urllib3.disable_warnings()
host = 'https://www.biqudu.com'
#获得搜索小说的url
def getnovalurl():
    req = requests.get('https://www.biqudu.com/searchbook.php',data=payload,headers=headers,verify = False)
    soup = BeautifulSoup(req.text,'lxml')
    urls = soup.find_all('a',href=re.compile(r'\/\d+_\d+\/'),height=False)
    for i in range(len(urls)):
        if i%2 != 0:
            src = re.sub('\s','',urls[i].text)
            if searchkey == src:
                global url,urlpath
                urlpath = urls[i]['href']
                url = parse.urljoin(host,urlpath)

#获得小说各章节url
def getchapterurls():
    requ = requests.get(url,headers=headers,verify = False)
    soup = BeautifulSoup(requ.text,'lxml')
    #print(soup.prettify())
    links = soup.find_all('a',href=re.compile(r'{}\d+\.html'.format(urlpath)))
    global urls
    for link in links:
        urlappend = parse.urljoin(host,link['href'])
        urls.add(urlappend)

def getcontent(i):
    #for i in range(len(urls)):
    resu = requests.get(urls[i],headers,verify=False)
    soup = BeautifulSoup(resu.text,'lxml')
    title = soup.find('h1').text
    content = soup.find('div', attrs={'id': 'content'})
    cont = re.sub(r'\s*|readx\(\)\;|chaptererror\(\)\;', '', content.text)
    with open(f'{path}\{i}.txt','w',encoding='utf-8') as f:
        f.write(f'{str(title)}\n{str(cont)}\n')
        print(f'write chapter {i} is over.')

def buildcontent():
    with open(f'{path}\{searchkey}.txt','a',encoding='utf-8') as ff:
        for i in range(len(urls)):
            with open(f'{path}\{i}.txt','r',encoding='utf-8') as f:
                content = f.read()
                ff.write(content)
            os.remove(f'{path}\{i}.txt')
    print('buildcontent finished.')

if __name__ == '__main__':
    pool = Pool(8)
    getnovalurl()
    getchapterurls()
    urls = list(urls)
    urls.sort()
    pool.map(getcontent,[i for i in range(len(urls))])
    buildcontent()