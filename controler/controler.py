#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(u'..')

from extractor.myappParser import MyappParser
from extractor.sjbaiduParser import SjbaiduParser
from extractor.zhushou360Parser import Zhushou360Parser
from util.mysqlWrapper import *
from util.browserHelper import *
import string
import urllib
import os
import requests

class Controler():
    def __init__(self):
        self._seeds_num = 100
        self._output_path = '../seeds/'
        self._db = 'taierdb'
        self.seeds =[]

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
    def get_seeds_by_search(self, keyword,domains):
        for domain in domains:
            if domain.startswith('http://sj.qq.com'):
                url = 'http://sj.qq.com/myapp/search.htm?kw={0}'.format(keyword)
                print url
                page = load_scroll_page(url)
                parser = MyappParser()
                self.generate_seeds(page,parser,domain)

            if domain.startswith('http://zhushou.360.cn'):
                nextpage = 1

                parser = Zhushou360Parser()
                is_pageend = False
                while not is_pageend:
                    url = 'http://zhushou.360.cn/search/index/?kw={0}&page={1}'.format(keyword,nextpage)
                    print url
                    response= requests.get(url)
                    page = response.text
                    if not page or response.status_code != requests.codes.ok:
                        is_pageend = True
                        print "eror to get url",url
                    else:
                        self.generate_seeds(page,parser,domain)
                        nextpage += 1
                        is_pageend = parser.is_pageEnd(page)


                #:TODO
            if domain.startswith('http://shouji.baidu.com'):
                parser = SjbaiduParser()
                nextpage = 1
                page = requests.get('http://shouji.baidu.com/s?wd={0}'.format(keyword)).text
                totalpage = int(parser.get_totalpage(page))
                while (nextpage <= totalpage):

                    url = 'http://shouji.baidu.com/s?wd={0}#page{1}'.format(keyword,nextpage)
                    print url
                    response = requests.get(url)
                    page = response.text
                    if not page or response.status_code != requests.codes.ok:
                        hasnext = False
                        print "eror to get url",url
                    else:
                        self.generate_seeds(page,parser,domain)
                        nextpage += 1



    def generate_seeds(self,page,parser,domain):
        for starturl in parser.extract_search_url(page):
                if starturl:
                    #检查seeds中是否已经有链接了
                    #TODO: is it neccessary????
                    inSeeds = False
                    conn = getConn(self._db)
                    sql = 'select url from app_Seeds'
                    url =  sqlExecute(sql, conn)
                    for each in url:
                        if starturl in each:
                            inSeeds = True
                    if (inSeeds ==False):
                        seed =[starturl,domain]
                        self.seeds.append(seed)
                        if len(self.seeds)>=self._seeds_num:
                            self.output_seeds(self.seeds)
                            self.seeds = []

    #监测下游是否抓取、反馈完毕,Ture 表示已经反馈完毕
    def get_crawler_stats(self):
        file_list = os.listdir(self._output_path)
        for file_name in file_list:
            if '.done' in file_name:
                return False
        return True
    #获取待抓取Domain
    def get_domain(self,conn):
        domains_str = []
        sql = 'select Domain from app_Conf'
        domains =  sqlExecute(sql, conn)
        for domain in domains:
            domains_str.append(domain[0])
        return domains_str

    #获取待抓取seeds
    def get_db_seeds(self):
        if self._output_path:
            if not self.get_crawler_stats():
                return
        else:
            print 'controler has no path error'

        conn = getConn(self._db)
        if conn:
            domains = self.get_domain(conn)

            for domain in domains:
                sql = "select URL, Domain from app_Seeds where Domain = '%s' and FetchTimes = 0 limit %d" % (domain, self._seeds_num)
                seeds =  sqlExecute(sql, conn)
            self.output_seeds(seeds)


    #输出种子文件
    def output_seeds(self,seeds):
        file_name = 'seeds_' + time.strftime('%Y-%m-%d--%H-%M-%S',time.localtime())
        path_file = self._output_path + file_name
        fd = open(path_file,'w')
        if fd:
            for seed in seeds:
                url = seed[0]
                domain = seed[1]
                fd.write('%s\t%s\n' % (url, domain))
            fd.close()
        else:
            print 'error'

        fddone = open(path_file + '.done','w')
        if fddone:
            fddone.close()
        else:
            print 'error'

    def get_start_seeds(self):
        if self._output_path:
            pass
            # if not self.get_crawler_stats():
            #     return
        else:
            print 'controler has no path error'

        if self._db:
            conn = getConn(self._db)
            if conn:
                domains = self.get_domain(conn)
                for keyword in self.get_keywords():
                    print keyword
                    self.get_seeds_by_search(keyword,domains)

    def main_work(self):
        pass

if "__main__" == __name__:
    controler = Controler()

    controler.get_start_seeds()
    #controler.get_db_seeds()