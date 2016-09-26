#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'
import lxml
import re
import lxml.html
from lxml import html

class XPath:

    xPaths = {
        "Name" : "//div[@class='det-name']/div[@class='det-name-int']/text()",

        "Screenshots": "//div[@class='pic-img-box']/img/@data-src",
        "Category": "//div[@class='det-type-box']/a[@class='det-type-link']/text()",
        "Developer": "//div[@class='det-othinfo-data' and @id='J_ApkPublishTime']/text()",
        "Description": "//div[@class='det-app-data-info']/text()|//div[@class='show-more-content text-body' and @itemprop='description']/div/p/text()",
        "Score": "//div[@class='com-blue-star-num']/text()",
        "Size":"//div[@class='det-size']/text()",
        "Ad":"//div[@class='det-adv adv-btn']/text()",
        "CommentCount":"//a[@class='det-comment-num']/a[@id='J_CommentCount']/text()",
        "Script":"//script[@type='text/javascript']/text()",
        # load by js,TODO
        "LastUpdateDate":"//div[@class='det-othinfo-data' and @id=['J_ApkPublishTime']/text()",
        "othinfo-data": "//div[@class='det-othinfo-data']/text()",
        "DeveloperUrls": "//div[@class='content contains-text-link']/a[@class='dev-link']",
        "RelatedApps": "//li[@class='det-about-app-box']//div[@class='app-right-data']/a[@class='appName']/@href",
        "SameDevApps":"//li[@class='det-samedeve-app-box']//div[@class='app-right-data']/a[@class='appName']/@href"
    }



class MyappParser:

    def parse_app_data(self, html):
        """
        Extracts relevant data out of the html received as argument

        :return: Dictionary mapping the app data
        """

        # Dictionary to Hold App's data
        app_data = dict()

        # Loading Html
        html_map = lxml.html.fromstring(html)

        # Reaching Useful Data

        scripts = self.extract_node_text(html_map, 'Script',True)
        for script in scripts:
            appDetailData =  re.findall(r"appDetailData",script)
            if appDetailData:
                app_data['apkName'] = re.findall(r"apkName.*\"(.*)\",",script)[0]
                app_data['name'] = re.findall(r"appName.*\"(.*)\",",script)[0]
                app_data['apkCode'] = re.findall(r"apkCode.*\"(.*)\",",script)[0]
                app_data['appId'] = re.findall(r"appId.*\"(.*)\",",script)[0]
                app_data['iconUrl'] = re.findall(r"iconUrl.*\"(.*)\",",script)[0]
                app_data['downTimes'] = re.findall(r"downTimes.*\"(.*)\",",script)[0]
                app_data['downUrl'] = re.findall(r"downUrl.*\"(.*)\",",script)[0]

        app_data['category'] = self.extract_node_text(html_map, 'Category')
        app_data['size'] = self.extract_node_text(html_map, 'Size')
        app_data['hasAd'] = self.extract_node_text(html_map, 'Ad')
        app_data['score'] = self.extract_node_text(html_map, 'Score')
        app_data['reviewCount'] = self.extract_node_text(html_map, 'CommentCount')
        #app_data['screenshots'] = self.extract_node_text(html_map, 'Screenshots', True)
        app_data['description'] = "\n".join(self.extract_node_text(html_map, 'Description', True))
        app_data['currentVersion'] = self.extract_node_text(html_map, 'othinfo-data',True)[0]
        app_data['developer'] = self.extract_node_text(html_map, 'othinfo-data',True)[1]

        return app_data

    def parse_related_apps(self, html):
        # Loading Html
        html_map = lxml.html.fromstring(html)

        # Reaching Useful Data
        xpath = XPath.xPaths['RelatedApps']
        nodes = html_map.xpath(xpath)
        '''
        for i in range(0,len(nodes)):
            nodes[i] = nodes[i].lstrip("..")
            '''

        nodes = map(lambda node: node.lstrip(".."),nodes)
        # Appending url prefix to the actual url found within the html
        return map((lambda url: '{0}{1}'.format('http://sj.qq.com', url)), nodes)

    def parse_samedev_apps(self, html):
        # Loading Html
        html_map = lxml.html.fromstring(html)

        # Reaching Useful Data
        xpath = XPath.xPaths['SameDevApps']
        nodes = html_map.xpath(xpath)
        '''
        for i in range(0,len(nodes)):
            nodes[i] = nodes[i].lstrip("..")
            '''

        nodes = map(lambda node: node.lstrip(".."),nodes)
        # Appending url prefix to the actual url found within the html
        return map((lambda url: '{0}{1}'.format('http://sj.qq.com', url)), nodes)

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
        xpath ="//div[@class='icon-margin']/a[@class='icon' and \
                @target='_blank']"
        tree = html.fromstring(page)
        urls = tree.xpath(xpath)
        if urls is None or len(urls) == 0:
            yield None

        # Go on each node looking for urls
        url_prefix = 'http://sj.qq.com/myapp/'
        for node in urls:
            if "href" in node.attrib and "detail.htm?apkName=" in node.attrib["href"]:
                url = node.attrib["href"]
                yield "{0}{1}".format(url_prefix, url.lstrip("../myapp"))


