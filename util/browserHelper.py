#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

#simulate browser scroll
def scroll(driver):
    driver.execute_script("""
        (function () {
            var y = document.body.scrollTop;
            var step = 100;
            window.scroll(0, y);
            function f() {
                if (y < document.body.scrollHeight) {
                    y += step;
                    window.scroll(0, y);
                    setTimeout(f, 50);
                }
                else {
                    window.scroll(0, y);
                    document.title += "scroll-done";
                }
            }

            setTimeout(f, 1000);
        })();
        """)
#loal all page content, used for myapps
def load_page(url):
    service_args = [
            '--load-images=no'
        ]
    browser = webdriver.PhantomJS(service_args=service_args)

    browser.set_page_load_timeout(30)
    try:
        browser.get(url)
        print ("crawling %s ......" %url)
    except Exception as e:
        print "oops something wrong"
        #if errors detected. rest for 10minutes
        time.sleep(600)

   #scroll the page to load more
    maxtime = 30
    timecount = 0
    while True:
        try:
            scroll(browser)
            time.sleep(1)
            timecount += 1
            ec = EC.text_to_be_present_in_element((By.CLASS_NAME, 'load-more-btn'), u'没有更多了')
            if ec.__call__(browser):
                break
            else:
                if timecount > maxtime:

                    break
                else:
                    pass
        except Exception as e:
            print e
            break
    whole_page = browser.page_source

    browser.close()
    return whole_page