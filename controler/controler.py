#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'

from util.mysqlWrapper import *
from util.browserHelper import *
import time
import string
import urllib
import os

import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(u'..')

class controler():
    def __init__(self):
        pass

    #构造搜索关键字
    def get_keywords(self):
        keywords = []
        #a-z
        [keywords.append(x) for x in string.ascii_lowercase]
        #汉字
        f = open('./ChineseCharacters','r')
        for line in f.readlines():
            for c in line.split():
                keywords.append(urllib.quote(c.decode('gbk').encode('utf-8')))
        f.close()
        for keyword in keywords:
            yield keyword

    #通过搜索关键字获得初始seeds
    def get_seeds_by_search(self):
        pass



    #监测下游是否抓取、反馈完毕,Ture 表示已经反馈完毕
    def get_crawler_stats(self,path):
        file_list = os.listdir(path)
        for file_name in file_list:
            if '.done' in file_name:
                return False
        return True


    #获取待抓取Domain
    def get_domain(conn):
        domains_str = []
        sql = 'select Domain from app_Conf'
        domains =  sqlExecute(sql, conn)
        for domain in domains:
            domains_str.append(domain[0])
        return domains_str

    #获取待抓取seeds
    def get_seeds_from_db(domains,conn):
        pass

    #输出种子文件
    def output_seeds(seeds,path):
        pass

    def mainwork(self,dbname, path):
        if path:
            if not self.get_crawler_stats(path):
                return
        else:
            print 'controler has no path error'

        if dbname:
            conn = getConn(dbname)
            if conn:
                domains = self.get_domain(conn)

if "__main__" == __name__:
    controler = controler()
    db = 'taierdb'
    output_path = '../seeds/'
    controler.mainwork(db, output_path)