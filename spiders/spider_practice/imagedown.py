from urllib import parse
from bs4 import BeautifulSoup
from gevent.pool import Pool
import requests
from lxml import etree
import re,os,time
import logging

path = r'F:\spiderresult\picture'#保存路径(根据自己电脑修改)

logging.basicConfig(level = logging.WARNING,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
origin_url = 'http://www.netbian.com'
searchurl = 'http://www.netbian.com/e/sch/index.php'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'}
payload = {'page':'0',
           'keyboard':'',
           'submit':''
           }
imageurls = set()
pages = ['0','1']


def geturlencode():#获取网站使用的编码
    req = requests.get(origin_url,headers=headers)
    urlencode = req.apparent_encoding
    return urlencode

def getsearchkey():
    codetype = geturlencode()
    # 对汉字进行网站使用的编码方式编码，防止编码错误无法解析正确url
    global payload
    payload['keyboard'] = input('Please input searchkey.').encode(codetype)
    if payload['keyboard'] == '':
        payload['keyboard'] = input("Please input searchkey another.").encode(codetype)
def getpages():#获取图片url
    req = requests.get(searchurl,params=payload,headers=headers)
    req.encoding = req.apparent_encoding
    time.sleep(0.3)
    source = etree.HTML(req.text)
    #获取页数
    page = source.xpath(u"//div[@class='page']/a")
    global pages
    for pa in page:
        pages.append((pa.text))
    pages = pages[:-2]


def getimgurls():
    for page in pages:
        payload['page']= page
        req = requests.get(searchurl,params=payload,headers=headers)
        req.encoding = req.apparent_encoding
        source = etree.HTML(req.text)
        # xpath定位到带有font属性的节点然后返回父节点，从父节点做起点获取节点对应的url
        links = source.xpath(u"//div[@class='list']/ul/li/b/a/font/../../../a")
        global imageurls
        for link in links:
            imageurl = parse.urljoin(origin_url,link.attrib['href'])
            imageurls.add(imageurl)

#将得到的url.path整合到url里
def buildurls():
    for i in range(len(imageurls)):
        requ = requests.get(imageurls[i],headers=headers)
        requ.encoding = requ.apparent_encoding
        requ = etree.HTML(requ.text)
        url = requ.xpath("//div[@class='pic']/p/a")
        imageurls[i] = parse.urljoin(origin_url,url[0].attrib['href'])

#下载url对应图片
def download():
    for i in range(len(imageurls)):
        imagename = i
        req = requests.get(imageurls[i],headers=headers)
        req.encoding = req.apparent_encoding
        req = etree.HTML(req.text)
        source = req.xpath("//td[@align='left']/a/img")
        image = str(re.findall(r'http://.*\.jpg',str(source[0].attrib))[0])
        req = requests.get(image,headers)
        req.encoding = req.apparent_encoding
        with open(f'{path}\{imagename}.jpg','wb') as f:
            f.write(req.content)
        logging.warning(f'{imagename}is downloaded.')

if __name__ == '__main__':
    getsearchkey()
    getpages()
    getimgurls()
    #对imageurls进行排序
    imageurls = list(imageurls)
    imageurls.sort()
    print(pages,imageurls)
    buildurls()
    download()
    print(f'{len(imageurls)} pictures is downloaded.')
