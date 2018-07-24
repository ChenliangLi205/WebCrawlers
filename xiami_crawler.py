# -*- coding:utf-8 -*-
from pyquery import PyQuery as pq
import networkx as nx
import argparse
import re
from Basic import BasicCrawler


# The Xiami Crawler is not runable yet because of the strong anti-crawl technique of Xiami.
# Hopefully this will be solved in the future.

def parse_args():
    """
    parse the arguments
    """
    parser = argparse.ArgumentParser(description="Run Douban Movie Crawler.")

    parser.add_argument(
        '--starting-url', nargs='+', help='Input the url(s) to start with.',
        default='https://www.xiami.com/song/2085229'
    )
    parser.add_argument(
        '--path', nargs='?', help='Input the path to save graph file and label file.',
        default='Data/Xiami/'
    )
    parser.add_argument(
        '--max-size', type=int, default=1, help='The approximate number of nodes in the network'
    )
    return parser.parse_args()


class XiamiCrawler(BasicCrawler):
    def __init__(self, max_size):
        super(XiamiCrawler, self).__init__()
        self.max_size = max_size
        self.graph = nx.Graph()
        self.interval = 5

    def process_page_data(self, page_data):
        """
        First obtain the name of the current song
        Then obtain the musician name as label
        Last extract the linked songs
        """
        self.obtain_song_name(page_data)
        self.obtain_musician_name(page_data)
        self.extract_linked_songs(page_data)

    @staticmethod
    def obtain_song_name(page_data):
        """ Obtain Song Name """
        doc = pq(page_data)
        items = doc('#title')
        song_name = items.find('h1').text()
        return song_name

    @staticmethod
    def obtain_musician_name(page_data):
        """ Obtain musician Name"""
        doc = pq(page_data)
        items = doc('#albums_info a')
        musician_name = items.eq(1).text()
        return musician_name

    @staticmethod
    def extract_linked_songs(page_data):
        """ Extract Songs That are Linked By The
            'People who like this song also enjoys'
            relationship
        """
        linked_songs = []
        linked_urls = []
        doc = pq(page_data)
        items = doc('.song_name a')
        i = 0
        linked_song = items.eq(i)
        while linked_song:
            linked_songs.append(linked_song.text())
            linked_urls.append(linked_song.attr('href'))
            i += 1
            linked_song = items.eq(i)
        return linked_songs, linked_urls


if __name__ == '__main__':
    args = parse_args()
    crawler = XiamiCrawler(args.max_size)
    crawler.start_with(args.starting_url)
    crawler.run()
