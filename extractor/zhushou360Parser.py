#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'
import lxml

import lxml.html
from lxml import html

class XPath:

    xPaths = {
        "Name" : "//h2[@id='app-name']/span/text()",
        "reviewCount":"//span[@class='js-comments review-count-all']/text()",
        "category": "//div[@class='app-tags']/a[@*]/text()",
        "description": "//div[@class='breif']/text()",
        "baseinfo": "//div[@class='base-info']//td/text()",

        "Score": "//div[@class='pf']/span[@class='s-1 js-votepanel']/text()",

        "downTimes":"//div[@class='pf']/span[@class='s-3']/text()",
        "size":"//div[@class='pf']/span[@class='s-3']/text()",
        "downUrl":"//dd/a[@*]/@href",
        "appId":"//dd/a[@*]/@data-sid",

        "iconUrl":"//dl[@class='clearfix']/dt/img/@src",
        #"guesslikeapps": "//ul[@id='likelist']//li/a[@class='click-log']/@href",
        "guesslikeapps": "//ul[@id='likelist']//li",
        "infors": "//div[@class='title']/ul/li/text()",
        "paidInfo": "//div[@class='tips-box blue' and @id='feePanel']/p/text()",

        "numPermissions": "//li[@class='item-3' and @id='authority-tg']/text()",
        "permissions": "//div[@class='tips-box red' and @id='authority-panel']/p/text()",

        "categoryhotapps": "//ul[@id='category-hot']//li/a[@class='click-log']/@href",


    }



class Zhushou360Parser:

    def parse_app_data(self, html):
        """
        Extracts relevant data out of the html received as argument
        :return: Dictionary mapping the app data
        """
        # Dictionary to Hold App's data
        app_data = dict()
        # Loading Html
        html_map = lxml.html.fromstring(html)

        app_data['name'] = self.extract_node_text(html_map, 'Name')
        app_data['category'] = self.extract_node_text(html_map, 'category',True)
        if app_data['category']:
            app_data['category'] = "-".join(app_data['category'])

        app_data['iconUrl'] = self.extract_node_text(html_map, 'iconUrl')
        app_data['downUrl'] = self.extract_node_text(html_map, 'downUrl')
        app_data['apkName'] = app_data['downUrl'].split('/')[-1].rstrip('.apk')
        app_data['appId'] = self.extract_node_text(html_map, 'appId')
        app_data['Score'] = self.extract_node_text(html_map, 'Score')
        # app_data['reviewCount'] = self.extract_node_text(html_map, 'reviewCount'):TODO: ALWAYS GOT 0
        app_data['downTimes'] = self.extract_node_text(html_map, 'downTimes',True)[0].lstrip(u'下载：')
        app_data['size'] = self.extract_node_text(html_map, 'size',True)[1]
        infors = self.extract_node_text(html_map, 'infors',True)
        app_data['isSecure'] = int((u'安全无毒') in infors)
        app_data['hasAd'] = int((u'有广告') in infors)
        app_data['hasPaid'] = int((u'免费')not in infors)
        app_data['numPermissions'] =  int(self.extract_node_text(html_map, 'numPermissions').split('：')[-1])
        app_data['paidInfo'] = self.extract_node_text(html_map, 'paidInfo')

        app_data['permissions'] = self.extract_node_text(html_map, 'permissions')


        # app_data['category'] = self.extract_node_text(html_map, 'Category',True)[2]
        app_data['description'] = self.extract_node_text(html_map, 'description', True)
        if app_data['description']:
            app_data['description'] = "\n".join(app_data['description'])

        baseinfo = self.extract_node_text(html_map, 'baseinfo', True)
        app_data['developer'] = baseinfo[0]
        app_data['lastUpdateDate'] = baseinfo[1]
        app_data['currentVersion'] = baseinfo[2]
        app_data['minimumOSVersion'] = baseinfo[3].lstrip('Android ')

        app_data['language'] = baseinfo[4]


        return app_data

    def parse_guess_like_apps(self, html):
        # Loading Html
        html_map = lxml.html.fromstring(html)
        # Reaching Useful Data
        xpath = XPath.xPaths['guesslikeapps']
        nodes = html_map.xpath(xpath)
        # Appending url prefix to the actual url found within the html
        return map((lambda url: '{0}{1}'.format('http://zhushou.360.cn', url)), nodes)

    def parse_category_hot_apps(self, html):
        # Loading Html
        html_map = lxml.html.fromstring(html)
        # Reaching Useful Data
        xpath = XPath.xPaths['categoryhotapps']
        nodes = html_map.xpath(xpath)
        # Appending url prefix to the actual url found within the html
        return map((lambda url: '{0}{1}'.format('http://zhushou.360.cn', url)), nodes)


    def extract_node_text(self, map, key, is_list=False):
        """
        Applies the XPath mapped by the "key" received, into the
        map object that contains the html loaded from the response
        """
        if key not in XPath.xPaths:
            return None

        xpath = XPath.xPaths[key]
        node = map.xpath(xpath)

        if not node:
            return None

        if not is_list:
            return node[0].strip()
        else:
            # Distinct elements found
            seen = set()
            return [x for x in node if x not in seen and not seen.add(x)]

    def extract_search_url(self,page):
        xpath ="//div[@class='SeaCon']/ul//li/dl/dt/a"
        tree = html.fromstring(page)
        urls = tree.xpath(xpath)
        if urls is None or len(urls) == 0:
            yield None

        # Go on each node looking for urls
        url_prefix = 'http://zhushou.360.cn'
        for node in urls:
            if "href" in node.attrib :
                url = node.attrib["href"]
                yield "{0}{1}".format(url_prefix, url)

    def is_pageEnd(self,page):

        xpath ="//div[@class='srtcon']/div[@class='nofd']/text()"
        tree = html.fromstring(page)
        pageend = tree.xpath(xpath)
        if pageend:
            if (u'没有找到相关应用') in pageend:
                return True

        return False


