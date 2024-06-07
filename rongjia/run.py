#!/usr/bin/env python3
# vim: set fileencoding: UTF-8 -*-

from json import loads
from urllib.request import quote, Request, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

class productinfo:
    def __init__(self) -> None:
        self.id = None
        self.name = None
        self.price = 0.0
        self.date = None
        self.unit = ''
        self.raw = None

    def __str__(self) -> str:
        return 'id=%s, name=%s, price=%0.2f, date=%s, unit=%s' % (self.id, self.name, self.price, self.date, self.unit)

class querier():
    def __init__(self) -> None:
        self.__URL = '''https://www.cdprice.cn/price/homePageAction!getAllType.do'''
        self.__REFER = '''https://www.cdprice.cn/price/homePageAction!getArticle.do?title=%s'''
        self.__cookiejar = CookieJar()
        self.__opener = build_opener(HTTPCookieProcessor(self.__cookiejar))

    def query(self, product: str)->str:
        referurl = self.__REFER % quote(quote(product))
        header = {
            'Referer': 'https://www.cdprice.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'
        }
        req = Request(referurl, method='GET', headers=header)
        with self.__opener.open(req) as rsp:
            pass
        data = ('title=%s' % quote(product)).encode('utf-8')
        data = b'''title=%E7%8C%AA%E8%82%89'''
        header = {
            'Referer': referurl,
            'Host': 'www.cdprice.cn',
            'Origin': 'https://www.cdprice.cn',
            'Content-Type': "application/x-www-form-urlencoded; charset=utf-8",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Content-Length': len(data),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en,zh-CN;q=0.5',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
        req = Request(self.__URL, data, method='POST', headers=header)
        #print(data)
        with self.__opener.open(req) as f:
            data = f.read().decode('UTF-8')
        return data

def parse(jsonstr: str)->list:
    jobj = loads(jsonstr)
    if jobj == None or type(jobj) != dict:
        raise TypeError('Web API respponse malformed')
    if 'list1' not in jobj:
        raise TypeError('"list1" not found')
    list1 = jobj['list1']
    if type(list1) != list:
        raise TypeError('"list1" is NOT a list')
    return [__createproduct(raw) for raw in list1]

def __createproduct(raw: dict)->productinfo:
    p = productinfo()
    p.raw = raw
    p.id = raw['cltpro01id']
    p.name = raw['cltpro01001']
    p.unit = raw['cltpro01005']
    p.date = raw['cltprc05001']
    p.price = raw['cltprc05007']
    return p

s=querier().query('猪肉')
products = parse(s)
for p in products:
    print(p)
