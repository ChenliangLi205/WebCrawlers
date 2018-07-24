# -*- coding:utf -*-
import pyquery as pq
import networkx as nx
from Basic import BasicCrawler


class Music163Crawler(BasicCrawler):
    def __init__(self, max_size):
        super(Music163Crawler, self).__init__()
        self.max_size = max_size
        self.graph = nx.Graph()
        self.interval = 10

    def process_page_data(self, page_data):
        """
        First obtain the name of the current song
        Then obtain the musician name
        Then the album name
        Last extract the linked songs
        """
        self.obtain_song_name(page_data)
        self.obtain_musician_name(page_data)
        self.obtain_album(page_data)
        self.extract_linked_songs(page_data)
