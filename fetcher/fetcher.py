#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'
import sys, os
import datetime


from util.MongoWrapper import MongoDBWrapper
from extractor.myappParser import MyappParser
from extractor.sjbaiduParser import SjbaiduParser
from extractor.zhushou360Parser import Zhushou360Parser


import logging
from util.browserHelper import *

import requests
import traceback
from nt import chdir
# from util.mysqlWrapper import getConn, insertRecord, loadRecord, getRecord, sqlExecute
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(u'..')
class fetcher:
    def __init__(self):
        self._seedsdir = u"../seeds"
        self._logdir = u"../log"
        self._mongowrapper = MongoDBWrapper()
        self._mongowrapper.connect('appdb')
        self._infocolection = 'app_Info'
        self._seedscolection = 'app_Seeds'

        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(message)s |---| %(levelname)s  %(filename)s[line:%(lineno)d]',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=u'{}/fetcher.log'.format(self._logdir),
                filemode='w')

        self.logger = logging.getLogger('FetcherLogger')
        self.logger.setLevel(logging.DEBUG)

    def get_from_url(self,url, suburl_filter):
        if not url:
            self.logger.warning(u"unvailable url: %s" % url)
            return False

        if url.startswith("https://"):
            return False

        real_url = url
        if not real_url.startswith("http://"):
            real_url = "http://" + real_url

        start_ts = time.time()
        self.logger.info(u"==FetchStart== {}, {}".format(start_ts, url))

        try:
            #real_url = 'http://zhushou.360.cn/detail/index/soft_id/3488793'
            print "start get page",datetime.datetime.now()
            response = requests.get(url=real_url)    # 最基本的GET请求
            page = response.text
            if not page or response.status_code != requests.codes.ok:
                self.logger.debug(u"Fetch failed with status code: {}".format(response.status_code))
                return False
            print "finish get page",datetime.datetime.now()
            #print real_url
            # page = load_page(real_url) :TODO 有一些js的数据抓不到
            if 'qq'in suburl_filter:
                app,sublink = self.fetch_myapp_app(page)
                print 'qq'
            if '360' in suburl_filter:
                print '360'
                app,sublink = self.fetch_zhushou360_app(page)

            if 'baidu'in suburl_filter:
                print 'baidu'
                app,sublink = self.fetch_sjbaidu_app(page)

            for key in app.keys():
                if app[key] is None:
                    app[key] = u''
            #app_data = [data or u'' for data in app]


            query = {"_id": url.strip(), "domain": suburl_filter}
            # print "start db info",datetime.datetime.now()
            # conn = getConn("taierdb")

            self._mongowrapper.find_and_modify(query,app,self._infocolection)


            self.store_suburls(sublink,url,suburl_filter)

            #:TODO: 根据不同的parser解析
                #TODO:update table app_info.,self.fetch_app()


        except Exception as e:
            print real_url
            print e

        self.logger.info(u"FetchEnd  {} {}".format(time.time() - start_ts, url))

        return True

    def fetch_myapp_app(self,page):
        parser = MyappParser()
        app = parser.parse_app_data(page)
        related_apps = parser.parse_related_apps(page)
        sameDev_apps = parser.parse_samedev_apps(page)

        related_apps.extend(sameDev_apps)
        return app,related_apps

    def fetch_sjbaidu_app(self,page):
        parser = SjbaiduParser()
        related_apps = parser.parse_related_apps(page)
        app = parser.parse_app_data(page)
        return app,related_apps

    def fetch_zhushou360_app(self,page):
        print "start zhushou parser",datetime.datetime.now()
        parser = Zhushou360Parser()
        app = parser.parse_app_data(page)
        print "stop zhushou parser",datetime.datetime.now()
        ## :TODO:360手机助手的链接是动态生成的，需要重新考虑
        related_apps = []
        # related_apps = parser.parse_guess_like_apps(page)
        # categoryhot_apps = parser.parse_category_hot_apps(page)

        # related_apps.extend(categoryhot_apps)
        return app,related_apps

    def get_seeds(self):

        seedfiles = os.listdir(self._seedsdir)
        for f in seedfiles:
            if not f.endswith(".done"):
                continue

            real_f = f.split(".done")[0]
            lines = list(file(self._seedsdir+"/"+real_f))
            numLine = len(lines)
            self.logger.debug(u"start file: real_f, with {} lines".format(numLine))

            for idxLine, line in enumerate(lines):
                url, suburl_filter = line.strip().split("\t", 2)
                self.logger.debug(u"start idxLine: {}/{}".format(idxLine, numLine))

                ret = False
                # conn = getConn("taierdb")
                # table = 'app_Seeds'

                try:

                    print "finish parsing txt",datetime.datetime.now()
                    ret = self.get_from_url(url, suburl_filter)
                    print "finish paring page",datetime.datetime.now()
                    query = {'_id':url}
                    # sql = u"""select errorTimes from app_Seeds where url = '{}'""".format(url);
                    # errorTimessql = sqlExecute(sql, conn)
                    errorTimessql = self._mongowrapper.query_one(query,self._seedscolection)
                    errorTimes=0
                    if errorTimessql:
                        if 'errorTimes'in errorTimessql.keys():
                            errorTimes = errorTimessql['errorTimes']

                    # if not errorTimessql[0]['errorTimes']:
                    #     errorTimes = 0
                    # else:
                    #     errorTimes = errorTimessql[0]['errorTimes'];

                    if ret:
                        query = {"_id": url.strip(), "domain": suburl_filter}
                        measures = {"fetchTimes": 1,"errorTimes":errorTimes}

                        # sql = u"""update app_Seeds set fetchTimes = 1 where url = '{}'""".format(url);
                    else:
                        # dimensions = {"url": url.strip(), "domain": suburl_filter}
                        errorTimes += 1
                        query = {"_id": url.strip(), "domain": suburl_filter}
                        measures = {"fetchTimes": 1,"errorTimes":errorTimes}
                        # sql = u"""update app_Seeds set errorTimes = errorTimes + 1, fetchTimes = 1 where url = '{}'""".format(url);

                except Exception as e:
                    self.logger.warning(str(e))
                    self.logger.warning(traceback.format_exc())
                    continue

                try:

                    self._mongowrapper.find_and_modify(query,measures,self._seedscolection)
                    print "addddddddddddda newlink"

                    #sqlExecute(sql, conn);

                except Exception as e:
                    self.logger.warning(str(e))
                    self.logger.warning(traceback.format_exc())

                # conn.close()
                # print "finish db seeds",datetime.datetime.now()

            name = self._seedsdir+"/"+real_f+'.fetched'
            chdir(os.path.dirname(self._seedsdir+"/"+real_f))
            os.rename(real_f,name)
            os.remove(real_f+'.done')


    def store_suburls(self,suburls, url, suburl_filter):
        # conn = getConn("taierdb")

        numSubLinks  = len(suburls)
        print "addddddddddddddddddddddddsublinkxs",numSubLinks
        # 如果没有extend的url，直接跳出
        if numSubLinks == 0:
            return False
        if not url:
            self.logger.warning("parentUrl is None")
            return False

        suburl_filter = suburl_filter.strip()
        query = {"parentUrl": url.strip()}

        # table="app_Seeds"
        numNewSubLinks = numSubLinks - self._mongowrapper.query_some(query, self._seedscolection).count()
        # numNewSubLinks = numSubLinks - len(getRecord(dimensions, table, conn=conn) or [])
        numNewSubLinks = (numNewSubLinks >= 0) and numNewSubLinks or 0

        dimensions = {"_id": url.strip(), "domain": suburl_filter}
        measures = {"numSubLinks": numSubLinks, "numNewSubLinks": numNewSubLinks}

        self._mongowrapper.find_and_modify(dimensions, measures,  self._seedscolection)


        for surl in suburls:
            if not surl:
                continue

            dimensions = {"_id": surl.strip()}
            measures = {"errorTimes": 0, "fetchTimes": 0, "parentUrl": url.strip(), "domain": suburl_filter}
            self._mongowrapper.find_and_modify(dimensions,measures,  self._seedscolection)

            # if not getRecord(dimensions, table, conn=conn):
            #     insertRecord(measures, dimensions, table, conn=conn)

        # conn.close()
        return True

if "__main__" == __name__:
    fetcher = fetcher()



    while True:
        print "start counting time",datetime.datetime.now()
        fetcher.get_seeds()
        time.sleep(10)
