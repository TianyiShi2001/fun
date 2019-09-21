#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "石天熠"

import re, os, csv, json, time, sys, threading
import requests
from wordcloud import WordCloud #,ImageColorGenerator,STOPWORDS
from tuchong_utils import _suggest_threads, _save_img, _run_threads

class TuchongQuery(object):

    def __init__(self, query):
        self.query = query # e.g. 'jk 少女'
        self.params = '+'.join(query.split(' ')) # e.g. 'jk+少女'
        self.post_list = self.get_post_list_raw()

    def get_post_list_raw(self):
        print('正在抓取与"' + self.query + '"相关的的所有作品的源信息...')

        page_number = 1
        post_list = []
        while True:
            url = 'https://tuchong.com/rest/search/posts?query=' + self.params + '&page=' + str(page_number) # e.g. https://tuchong.com/rest/search/posts?query=JK+少女&page=1
            j = requests.get(url).json() 
            next_post_list = j['data']['post_list']

            if next_post_list: # 若page_number大于最大页数，j['post_list']将为空
                post_list += next_post_list
                print('完成第', page_number, '页', sep='')
                page_number += 1
            else:
                print('完成。')
                return post_list
    
    def _mkdir(self, type):
        path = self.query + '/'
        if not os.path.exists(path):
                os.mkdir(path)
        path = path + type + '/'
        if not os.path.exists(path):
                os.mkdir(path)
        return path

    def get_all_info(self, out = 'csv'):
        path = self._mkdir('data')
        self.get_post_info(out = out)
        with open(path + 'post_list.json', 'w') as fp:
            json.dump(self.post_list, fp, ensure_ascii=False)

    def get_post_info(self, out = None):
        """从所有原始数据中提取post的信息
        """
        print('正在提取与"' + self.query + '"相关的的所有posts的信息...')
        path = self._mkdir('data')
        path += 'post_info'

        post_info = [] # a list containing dicts of individual post info
        field = ['post_id', 'author_id', 'published_at', 'image_count', 'favorites', 'comments']
        for post in self.post_list:
            new_post_info = [] # every individual is a list
            for item in field:
                new_post_info.append(post[item])
            post_info.append(new_post_info)
        if out is None:
            print('完成。')
            return post_info
        elif out == 'json':
            path += '.json'
            with open(path, 'w') as fp:
                json.dump(post_info, fp)
        elif out == 'csv':
            path += '.csv'
            with open(path, 'w') as fp:
                fp.write('#' + time.strftime('%Y-%m-%d') + '\n')
                writer = csv.writer(fp) # write head
                writer.writerow(field)
                for individual in post_info: # every individual is a list
                    writer.writerow(individual)
        print('数据已写入' + path)

    def get_images(self, sort = True, rank = True):
        pass

    def get_tag_wordcloud(self):
        print('正在生成词云')
        path = self._mkdir('data')
        path += 'wordcloud.jpg'

        tag_s = []
        for post in self.post_list:
            for tag in post['tags']:
                tag_s.append(tag['tag_name'])
        
        txt = ' '.join(tag_s)

        cloud = WordCloud(font_path='SourceHanSerifCN-Light.otf',
                          background_color='white',
                          margin=5, width=1920, height=1080)
        
        cloud.generate(txt).to_file(path)
        print('词云已写入' + path)


        # https://tuchong.com/rest/search/posts?query=JK&count=20&page=1

    
if __name__ == "__main__":
    q = TuchongQuery('jk 少女')
    q.get_tag_wordcloud
        
