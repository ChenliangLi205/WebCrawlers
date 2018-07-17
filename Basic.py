#-*- coding:utf-8 -*-
import urllib.parse
import urllib.request
import urllib.error
import time
from collections import deque
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class BasicCrawler(object):
    """
    基本的爬虫小框架， 用的话只要把process_page_data这个函数重写了就行
    """
    def __init__(self):
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.url_queue = deque()
        self.crawl_count = 0
        self.visited = set()
        self.current_url = None
        self.time_sleep = 3600

    def start_with(self, url):
        """
        :param url: str or list, the url(s) to start with
        :return:
        """
        if isinstance(url, str):
            self.url_queue.append(url)
            return
        if isinstance(url, list):
            for u in url:
                if isinstance(u, str):
                    self.url_queue.append(u)
                else:
                    raise TypeError("Invalid Url Type")
            return
        raise TypeError("Invalid Url Type")

    def request(self):
        """
        :return: the request
        """
        request = urllib.request.Request(
            url=self.current_url,
            data=None,
            headers=self.headers
        )
        return request

    def retrieve(self):
        """
        :return: the page data
        """
        try:
            data = urllib.request.urlopen(self.request()).read().decode('utf-8')
        except:
            print('failed to open url %s' % self.current_url)
            print('probably ip blocked, trying again in one hour...')
            time.sleep(self.time_sleep)
            self.url_queue.appendleft(self.current_url)
            return
        return data

    def get_page_data(self):
        """
        get page data
        """
        if len(self.url_queue):
            self.current_url = self.url_queue.popleft()

            if self.current_url not in self.visited:
                print("crawling url %s, %d urls crawled" % (self.current_url, len(self.visited)))
                self.visited.add(self.current_url)
                return self.retrieve()
            else:
                return
        else:
            return

    def run(self):
        """
        Bu Zhi Dao Gai Gan Shen Me
        """
        page_data = self.get_page_data()
        while page_data:
            self.process_page_data(page_data)
            page_data = self.get_page_data()
        return

    def process_page_data(self, page_data):
        """sha ye bu gan"""
        pass
