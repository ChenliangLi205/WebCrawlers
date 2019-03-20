# -*- coding: utf-8 -*-
import urllib.parse
import urllib.request
import urllib.error
from selenium import webdriver
import ssl
from bs4 import BeautifulSoup
import json
import time

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}

def GetHomePageDataFromChrome(url):
    chrome = webdriver.Chrome()
    try:
        chrome.get(url)
        pageData = chrome.page_source
    except:
        print("Error occurs when opening the home page %s" % url)
        chrome.quit()
        return
    else:
        chrome.quit()
        return pageData

def GetPageData(url, timeout=10, decode='gbk', waiting_secs=9):
    time.sleep(waiting_secs)
    request = urllib.request.Request(url=url, data=None, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except:
        print("failed to open url %s" % url)
        return
    else:
        byteData = response.read()
        try:
            decoded = byteData.decode(decode)
        except:
            print("failed to decode page data into %s" % decode)
            return
        else:
            print("succeed in opening and decoding page %s" % url)
            return decoded

def ExtractNewsLinksFrom(homepage="https://news.163.com"):
    homePageData = GetHomePageDataFromChrome(homepage)
    if homePageData is None:
        return
    soup = BeautifulSoup(markup=homePageData, features="html.parser")

    finds = soup.find_all('div',attrs={'class':'news_title'})
    newsUrls, newsTitles = [], []
    for div in finds:
        a = div.find('a')
        newsUrls.append(a.get('href'))
        newsTitles.append(a.text)
    return newsUrls, newsTitles

def GetNewsType(url):
    urlParts = url.split('/')
    domainNames = urlParts[2].split('.')
    if domainNames[1] != '163':
        return 'rubbish'
    if urlParts[3] == 'photoview':
        return 'photo'
    return 'article'

def GetArticleNewsCommentJson(url, commentsNumberLimit=40):
    newsId = GetArticleNewsId(url)
    commentJsonUrl = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/' \
                  'threads/%s/comments/hotList?ibc=newspc&limit=%d' \
                  '&showLevelThreshold=72&headLimit=1&tailLimit=2&offset=0&' \
                     'callback=jsonp_1551932636931&_=1551932636932' % (newsId, commentsNumberLimit)
    jsonPageData = GetPageData(commentJsonUrl, decode='utf-8')
    return jsonPageData

def SplitNewsIntoArticlePhoto(newsUrls, newsTitles):
    ''' Return a url->title dictionary'''
    articleBasedUrl2Title = dict()
    photoBasedUrl2Title = dict()
    for url, title in zip(newsUrls, newsTitles):
        newsType = GetNewsType(url)
        if newsType == 'photo':
            if url in photoBasedUrl2Title:
                continue
            photoBasedUrl2Title[url] = title
            continue
        if newsType == 'article':
            if url in articleBasedUrl2Title:
                continue
            articleBasedUrl2Title[url] = title
    return articleBasedUrl2Title, photoBasedUrl2Title

def GetArticleNewsId(url):
    newsLastPart = url.split('/')[-1]
    return newsLastPart.split('.')[0]

def JsonStripParenthese(jsondata):
    p1 = 0
    p2 = len(jsondata)-1
    while p1 <= p2:
        if jsondata[p1] == '(':
            p1 += 1
            break
        p1 += 1
    while p2 > p1:
        if jsondata[p2] == ')':
            break
        p2 -= 1
    return jsondata[p1:p2]

def GetContentfromJasonDicts(url2dict):
    '''Get content strings from jason, return a url->contents dictionary'''
    url2contents = dict()
    for url, jasonDict in url2dict.items():
        if url in url2contents:
            continue
        url2contents[url] = []
        if len(jasonDict['commentIds']) <= 0:
            continue
        for Id in jasonDict["comments"]:
            url2contents[url].append(jasonDict["comments"][Id]["content"])
    return url2contents

def GetJasonDicts(urls):
    ''' Get Jason file and turn it into dict for article based news'''
    url2dict = dict()
    for i,url in enumerate(urls):
        if url in url2dict:
            continue
        commentJson = GetArticleNewsCommentJson(url)
        if commentJson is None:
            continue
        commentJson = JsonStripParenthese(commentJson)
        jsonDict = json.loads(commentJson)
        url2dict[url] = jsonDict
    return url2dict

def GetCommentsfromUrls(urls):
    '''Get comment strings from news urls'''
    url2dict = GetJasonDicts(urls)
    url2comments = GetContentfromJasonDicts(url2dict)
    return url2comments

def main():
    newsUrls, newsTitles = ExtractNewsLinksFrom()
    articleUrl2Title, photoUrl2Title =\
        SplitNewsIntoArticlePhoto(newsUrls, newsTitles)
    url2comments = GetCommentsfromUrls(articleUrl2Title.keys())
    for url in url2comments:
        if url not in articleUrl2Title:
            print("Some Thing Ain't Right")
            continue
        print("标题：%s" % articleUrl2Title[url])
        for comment in url2comments[url]:
            print(comment)

if __name__ == '__main__':
    main()