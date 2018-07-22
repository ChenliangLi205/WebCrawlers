#-*- coding:utf-8 -*-
from pyquery import PyQuery as pq
import networkx as nx
import argparse
import re
from Basic import BasicCrawler


def parse_args():
    """
    parse the arguments
    """
    parser = argparse.ArgumentParser(description="Run Douban Movie Crawler.")

    parser.add_argument(
        '--starting-url', nargs='+', help='Input the url(s) to start with.',
        default='https://movie.douban.com/subject/1292052/?from=subject-page'
    )
    parser.add_argument(
        '--path', nargs='?', help='Input the path to save graph file and label file.',
        default='Data/Douban/'
    )
    parser.add_argument(
        '--max-size', type=int, default=200, help='The approximate number of nodes in the network'
    )
    return parser.parse_args()


class DoubanCrawler(BasicCrawler):
    def __init__(self, max_size):
        """
        :param max_size: maximum amount of nodes in the graph
        """
        super(DoubanCrawler, self).__init__()
        self.max_size = max_size
        self.count = 0
        self.styles = ["爱情片", "动作片", "战争片", "犯罪片",
                       "动画片", "悬疑片", "喜剧片", "科幻片"]
        self.count_styles = {}
        self.node_styles = {}
        for s in self.styles:
            self.count_styles[s] = 0
        self.graph = nx.Graph()
        self.attr_graph = nx.Graph()

    def start_with(self, url):
        """
        :param url: str or list, the url(s) to start with
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

    def process_page_data(self, page_data):
        """
        fetch style for the current movie
        get the movies that are linked to the current one
        """
        styled = self.styling(page_data)
        if styled:
            self.linking(page_data)
            self.tagging(page_data)

    @staticmethod
    def get_linked_url(page_data):
        """ get the linked urls of the current one"""
        url_dd = pq(page_data)('body').find('div').filter('.recommendations-bd')('dd')
        urls = []
        i = 0
        url_a = url_dd.eq(i)
        while url_a:
            url = url_a('a').attr('href')
            urls.append(url)
            i += 1
            url_a = url_dd.eq(i)
        return urls

    @staticmethod
    def get_tags(page_data):
        """
        fetch tag for the current movie
        """
        doc = pq(page_data)
        items = doc('.tags-body')
        tags = items.find('a').text()
        return tags

    @staticmethod
    def get_genres(page_data):
        """
        fetch genre of the movie
        """
        genres = []
        doc = pq(page_data)
        items = doc('.rating_betterthan')
        a_s = items.find('a').text()
        r = re.compile(r'% .+?片')
        for ele in r.findall(a_s):
            genre = ele.replace('% ', '')
            genres.append(genre)
        return genres

    def linking(self, page_data):
        """
        get the movies that are linked to the current one
        """
        urls = self.get_linked_url(page_data)
        max_size = self.max_size
        graph = self.graph
        for u in urls:
            if graph.number_of_nodes() > max_size:
                break
            if u in self.visited:
                continue
            if u not in graph.nodes():
                self.url_queue.append(u)
            graph.add_edge(u, self.current_url)

    def styling(self, page_data):
        """
        fetch genre for the current movie
        """
        styles = self.styles
        count_styles = self.count_styles
        current_url = self.current_url
        genres = self.get_genres(page_data)
        for g in genres:
            if g in styles:
                print('%s is %s' % (current_url, g))
                self.node_styles[current_url] = g
                count_styles[g] += 1
                return True
        print('Cannot get the type of this movie')
        self.graph.remove_node(current_url)
        return False

    def tagging(self, page_data):
        """
        fetch tags of the current movie
        and adding edges and nodes into the attributed graph
        """
        attr_graph = self.attr_graph
        current_url = self.current_url
        tags = self.get_tags(page_data)
        for t in tags:
            attr_graph.add_edge(current_url, t)

    def show_graph_attributes(self):
        """
        Show the current amount of nodes, edges in the graphs
        """
        count_styles = self.count_styles
        print('# of nodes', self.graph.number_of_nodes())
        print('# of links', self.graph.number_of_edges())
        print('# of attributes', self.attr_graph.number_of_nodes()-self.graph.number_of_nodes())
        for key, count in count_styles.items():
            print(key, count)

    def save(self, path):
        """
        Saving the movie graph and attributed graph and node labels into three files
        """
        graph_file = 'graph.edgelist'
        attrgraph_file = 'attrgraph.edgelist'
        nodelabel_file = 'labels.txt'
        node_styles = self.node_styles
        graph = self.graph
        nx.write_edgelist(G=graph, path=path+graph_file, data=False)
        nx.write_edgelist(G=graph, path=path+attrgraph_file, data=False)
        with open(path+nodelabel_file, 'w') as f:
            for node in graph.nodes():
                f.writelines('%s %s\n' % (node, node_styles[node]))


if __name__ == "__main__":
    """
    To run douban crawler:

    python douban_crawler.py --starting-url (The url of page to start with) --max-size 20 --path (The path to put files in)

    """
    args = parse_args()
    crawler = DoubanCrawler(args.max_size)
    crawler.start_with(args.starting_url)
    crawler.run()
    crawler.show_graph_attributes()
    crawler.save(path=args.path)
