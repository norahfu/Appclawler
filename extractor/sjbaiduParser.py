#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'
import lxml
import re
import lxml.html
from lxml import html

class XPath:

    xPaths = {
        "Name" : "//h1[@class='app-name']/span/text()",
         "Category": "//span/a[@target='_self']/text()",
        "Description": "//div[@class='brief-long']/p[@class='content content_hover']/text() |"
                       "//div[@class='brief-long']/p[@class='content']/text()"
        ,
        "Score": "//span[@class='star-percent']/@style",
        "Size":"//div[@class='detail']/span[@class='size']/text()",
        "downTimes":"//div[@class='detail']/span[@class='download-num']/text()",
        "currentVersion":"//div[@class='detail']/span[@class='version']/text()",
        "appfeaturedetail":"//div[@class='content-right']/div[@class='app-feature']/span[@class='app-feature-detail']/span[@class='res-tag-ok']/text() | "
                           "div[@class='content-right']/div[@class='app-feature']/span[@class='app-feature-detail']/span[@class='res-tag-warning']/text()",
        "downUrl":"//div[@class='area-download']/a[@class='apk']/@href",
        "iconUrl":"//div[@class='app-pic']/img[@*]/@src",
        "RelatedApps": "//div[@class='app-bd show']//@href",

    }



class SjbaiduParser:

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

        app_data['category'] = self.extract_node_text(html_map, 'Category',True)[2]
        appfeaturedetail = self.extract_node_text(html_map, 'appfeaturedetail',True)
        app_data['hasAd'] = int((u'含广告') in appfeaturedetail)
        app_data['isSecure'] = int((u'安全') in appfeaturedetail)
        app_data['size'] = self.extract_node_text(html_map, 'Size').lstrip(u'大小：')
        app_data['currentVersion'] =self.extract_node_text(html_map, 'currentVersion').lstrip(u'版本：')
        app_data['downTimes'] =self.extract_node_text(html_map, 'downTimes').lstrip(u'下载次数：')

        app_data['score'] = self.extract_node_text(html_map, 'Score').lstrip('width:')
        app_data['downUrl'] = self.extract_node_text(html_map, 'downUrl')
        app_data['iconUrl'] = self.extract_node_text(html_map, 'iconUrl')


        app_data['description'] = "\n".join(self.extract_node_text(html_map, 'Description', True))

        return app_data

    def parse_related_apps(self, html):
        # Loading Html
        html_map = lxml.html.fromstring(html)
        # Reaching Useful Data
        xpath = XPath.xPaths['RelatedApps']
        nodes = html_map.xpath(xpath)
        # Appending url prefix to the actual url found within the html
        return map((lambda url: '{0}{1}'.format('http://shouji.baidu.com', url)), nodes)


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
        xpath ="//div[@class='app']/div[@class='icon']/a[@target='_blank']"
        tree = html.fromstring(page)
        urls = tree.xpath(xpath)
        if urls is None or len(urls) == 0:
            yield None

        # Go on each node looking for urls
        url_prefix = 'http://shouji.baidu.com'
        for node in urls:
            if "href" in node.attrib :
                url = node.attrib["href"]
                yield "{0}{1}".format(url_prefix, url)

    def get_totalpage(self,page):

        xpath ="//input[@class='total-page']/@value"
        tree = html.fromstring(page)
        totalpage = tree.xpath(xpath)[0]

        return totalpage


