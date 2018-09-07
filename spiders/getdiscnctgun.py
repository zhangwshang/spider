import requests
import time
from bs4 import BeautifulSoup
import lxml
import re,os
import datetime


headers = {'Host': 'winlineev.com',
           'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language':'zh-CN',
           'Accept-Encoding': 'gzip, deflate',
           'Referer': 'http://winlineev.com/internet-admin/login',
           'Content-Type': 'application/x-www-form-urlencoded',
           'Content-Length': '39',
           "Cookie":'JSESSIONID=5F0DB9C34116A0847C9D70E413C5C72A; REFRESH-HEADER=TRUE',
           'Connection': "keep-alive",
           'Upgrade-Insecure-Requests': '1'}

loginurl = '###########################'#登陆url
gunurl = '######################################'form提交url
path = r'D:\desktopdata'
postdata = {'j_username':'####',
            'j_password':'####'}

formdata = {'gunCode':'',#枪编号
            'electricPile.site.id':'',#站点名
            'electricPile.id':'',#电桩号
            'state': '',#状态
            'gunConnectionStatus': '0',#枪状态
            'carConnectionStatus':'',#车状态
            'pager.offset':10#页码*10
            }

def login():#登陆平台
    conn = requests.session()
    req = conn.post(loginurl,data=postdata,headers=headers)
    return conn

def getdiscnctcount(conn,sitenub):#获取枪状态断开总数
    if sitenub not in [12,50,66,67]:#筛选去除不要站点数据
        formdata['electricPile.site.id'] = sitenub
        req = conn.post(gunurl,data=formdata)
        soup = BeautifulSoup(req.text,'lxml')
        nub = soup.find_all('font',attrs={'color':'red'})
        try:
            discnctcount = int(nub[-1].text)
            return discnctcount
        except:
            discnctcount = 0
            return discnctcount
    else:
        discnctcount = 0
        return discnctcount

def pagecount(discnctcount):#获取网页数
    a = discnctcount // 10
    b = discnctcount % 10
    if b == 0:
        maxpage = a
    else:
        maxpage = a+1
    return maxpage

def getkeymsg(conn,maxpage):#获取关键信息
    for i in range(maxpage):
        formdata['pager.offset'] = i*10
        req = conn.post(gunurl,data=formdata)
        soup = BeautifulSoup(req.text,'lxml')
        qbhs = soup.find_all('a', attrs={'data-rel': 'colorbox'})#获取枪编号，所有枪编号存储到allqbhs
        res = re.compile(u'\w{1,10}号桩|客户演示桩|\w{2,10}号充电桩|\s空闲\s|\s正准备充电\s|\s充电进行中\s|\s充电结束\s'
                          u'|\s启动失败\s|\s预约状态\s|\s系统故障\s|\s断开\s|\s连接\s|\s半连接\s')
        sults = re.findall(res,req.text)#获取枪信息
        resu = []
        #将信息中\r清除
        for ci in range(len(sults)):
            resu.append(re.sub(r'\r', '', sults[ci]))

        try:
            with open(rf'{path}\{sitenub}page{i+1}.txt', 'w',encoding='utf-8') as f:
                for num in range(len(qbhs)):
                    f.write(f'{qbhs[num].text}\t{resu[num*4]}{resu[num*4+1]}{resu[num*4+2]}{resu[num*4+3]}\n')
                print(f'{sitenub}page{i+1} is finished.')
        except:
            print(f'{qbhs}\nlenth:qbhs{len(qbhs)}\n')
            print(f'{resu}\nlenth:resu{len(resu)}\n')

def writetitle():
    date = datetime.datetime.now().date()
    hour = datetime.datetime.now().hour
    with open(rf'{path}\{date}-{hour}点.txt', 'w', encoding='utf-8') as ff:
        ff.write(u'枪编号\t场站名\t状态\t枪状态\t车状态\n')
def buildtext(maxpage):
    date = datetime.datetime.now().date()
    hour = datetime.datetime.now().hour
    with open(rf'{path}\{date}-{hour}点.txt', 'a',encoding='utf-8') as ff:
        for num in range(1, maxpage + 1):
            with open(rf'{path}\{sitenub}page{num}.txt','r',encoding='utf-8') as f:
                cont = f.read()
                ff.write(cont)
            os.remove(f'{path}\{sitenub}page{num}.txt')
    print('build finished.')

if __name__ == '__main__':
    writetitle()
    conn = login()
    for sitenub in range(1,68):
        discnctcount = getdiscnctcount(conn,sitenub)
        maxpage = pagecount(discnctcount)
        getkeymsg(conn, maxpage)
        buildtext(maxpage)