#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "石天熠"

import re, os, csv, json, time, sys, threading
import requests
from wordcloud import WordCloud #,ImageColorGenerator,STOPWORDS
from tuchong_utils import _suggest_threads, _save_img, _run_threads
#import urllib.request

class TuchongUser(object):

    def __init__(self, home_url):
        self.home_url = home_url # 如'https://tuchong.com/13044147/posts/'或'tuchong.com/13044147/posts'或'https://asamurai.tuchong.com/posts'
        id = re.findall(r'/(\d+)/', home_url) # 如'13044147'
        if id:
            self.user_id = id[0]
        else: # to deal with 'https://asamurai.tuchong.com/posts' etc.
            html = requests.get(home_url).text
            self.user_id = re.findall('"site_id":"(\\d+)"', html)[0]
        self.post_list = self.get_post_list_raw()
        self.username = self.post_list[0]['site']['name']
        self.followers = self.post_list[0]['site']['followers']

    def get_post_list_raw(self):
        """通过主页爬取所有原始数据
        """
        print('正在抓取id为"' + self.user_id + '"的用户的所有作品的源信息...')

        page_number = 1
        post_list = []
        while True:
            url = 'https://tuchong.com/rest/2/sites/' + self.user_id + '/posts?&page=' + str(page_number)
            j = requests.get(url).json()
            next_post_list = j['post_list']

            if next_post_list: # 若page_number大于最大页数，j['post_list']将为空
                post_list += next_post_list
                page_number += 1
            else:
                print('完成。')
                return post_list

    def _mkdir(self, type):
        path = self.user_id + '-' + self.username + '/'
        if not os.path.exists(path):
                os.mkdir(path)
        path = path + type + '/'
        if not os.path.exists(path):
                os.mkdir(path)
        return path

    def get_all_info(self, out = 'csv'):
        path = self._mkdir('data')
        self.get_author_info(out = out)
        self.get_post_info(out = out)
        self.get_tag_info(out = out)
        self.get_tag_wordcloud()
        with open(path + 'post_list.json', 'w') as fp:
            json.dump(self.post_list, fp, ensure_ascii=False)

    def get_author_info(self, out = None):
        print('正在提取用户"' + self.username + '"的个人信息...')
        path = self._mkdir('data')
        path += 'author_info'

        author_info = [self.user_id, self.username, self.followers]
        if out is None:
            print('完成。')
            return author_info
        elif out == 'json':
            path += '.json'
            with open(path, 'w') as fp:
                json.dump(author_info, fp)
        elif out == 'csv':
            path += '.csv'
            with open(path, 'w') as fp:
                writer = csv.writer(fp)
                writer.writerow(['user_id', 'username', 'followers'])
                writer.writerow(author_info)
        print('数据已写入' + path)

    def get_post_info(self, out = None):
        """从所有原始数据中提取post的信息
        """
        print('正在提取用户"' + self.username + '"的各个post信息...')
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

    def get_tag_info(self, out = None):
        """从所有原始数据中提取tag的信息
        """
        print('正在提取用户"' + self.username + '"的各个tag信息...')
        path = self._mkdir('data')
        path += 'tag_info'

        tag_info = []
        for post in self.post_list:
            for tag in post['tags']:
                tag_info.append([post['post_id'], tag['tag_name']]) # append instances in the form of [post_id, tag_name]
        if out is None:
            return tag_info
        elif out == 'json':
            path += '.json'
            with open(path, 'w') as fp:
                json.dump(tag_info, fp)
        elif out == 'csv':
            path += '.csv'
            with open(path, 'w') as fp:
                fp.write('#' + time.strftime('%Y-%m-%d') + '\n')
                writer = csv.writer(fp)
                writer.writerow(['post_id', 'tag'])
                for instance in tag_info:
                    writer.writerow(instance)
        print('数据已写入' + path)

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



    def get_post_urls(self):
        post_urls = []
        for post in self.post_list:
            post_urls.append(post['url'])
        return post_urls

    def get_image_urls(self, sort = True):
        print('正在提取用户"' + self.username + '"的所有图片链接...')
        if sort:
            id_and_image_urls = {}
            for post in self.post_list:
                this_post_urls = [] # each post can have multiple images
                for image in post['images']: # looping over the list of images of this post
                    image_url = image['source']['lr'] # e.g. https://tuchong.pstatp.com/33937/lr/397648555.jpg
                    image_url = re.sub('/lr/', '/f/', image_url) # convert to 'full' size
                    this_post_urls.append(image_url)
                id = post["published_at"][0:10] + '-' + post['post_id'] # 时间和post_id作为id
                id_and_image_urls.update({id:this_post_urls})
            print('完成。')
            return id_and_image_urls
        else:
            image_urls = re.findall("'lr': '(.+?)',", str(self.post_list))
            image_urls = list(map(lambda image_url:re.sub('/lr/', '/f/', image_url), image_urls))
            print('完成。')
            return(image_urls)

    def get_images(self, threads = 'auto', sort = True):
        print('正在下载用户"' + self.username + '"的所有图片...')

        # 创建存放图片的文件夹，名为`<用户id>-<用户名>`

        path = self._mkdir('img')

        if sort: # 需要整理
            # get urls as {time-post_id_1:[url1, url2], time-post_id_2:[url1, url2, ...], ...}
            id_and_urls = self.get_image_urls(sort = True)

            # 决定线程数
            if isinstance(threads, int): # 如果指定线程数
                threads = threads
            else: # 默认的自动
                threads = _suggest_threads(len(id_and_urls), 3)

            # 不断下载id_and_urls中的posts
            def download_post(path = path):
                try:
                     this_post = id_and_urls.popitem()
                except KeyError: # when dict is empty
                    sys.exit() # 结束线程
                id, url_s = this_post[0], this_post[1]
                total = len(url_s)
                print('正在下载post', id)
                path = path + id + '/'
                if not os.path.exists(path):
                    os.mkdir(path)
                for i, url in enumerate(url_s, start=1):
                        img_path = path + str(i) + '.jpg'
                        _save_img(url, img_path)
                        print(i, '/', total, ' of post ', id, ' from ', threading.current_thread().name, sep='')
                download_post() # 递归
            # 多线程
            _run_threads(n = threads, target=download_post)
            print('完成。')
        else: # 如果不需要整理
            image_urls = self.get_image_urls(sort = False)

            if isinstance(threads, int): # 如果指定线程数
                threads = threads
            else: # 默认的自动
                threads = _suggest_threads(len(image_urls), 8)
            
            def download_image():
                try:
                    url = image_urls.pop()
                except IndexError: # when empty
                    sys.exit()
                print('正在下载', url)
                filename = re.findall(r'\d+\.jpg', url)[0] # `<https://tuchong.pstatp.com/<user_id>/f/<image_id>.jpg
                # urllib.request.urlretrieve(url, 'img/' + self.username + '-' + str(i) + '.jpg')
                with open(path + filename, 'wb') as img:
                    img.write(requests.get(url).content)
                download_image()
                

            _run_threads(n = threads, target=download_image)

            print('完成。')






if __name__ == "__main__":
    print('欢迎使用石天熠的图虫信息爬取程序。在命令行使用时，可以用于\n\t（1）下载某个作者的全部图片，或者\n\t（2）获取作者及其全部作品的信息，并以json格式保存，同时整理重要信息，以json或csv格式保存，以及根据作者使用的tags生成词云，以jpg格式保存。')
    task = input('输入1或者2以继续。')
    home_url = input('请输入作者的主页链接，或者跳过以使用作者（石天熠）的图虫主页链接："https://tuchong.com/13044147/posts/"：')
    if not home_url:
        home_url = 'https://tuchong.com/13044147/posts/'
    site = TuchongUser(home_url)

    if task == '1':
        sort = input('是否按照"用户id-用户名/作品id/图片序号.jpg"的结构进行整理？（请输入y或者n）')
        threads = input('你想创建多少个线程用于下载？输入一个数字，或者跳过以自动决定线程数。')
        if sort == 'y':
            if not threads:
                site.get_images()
            else:
                site.get_images(threads=int(threads))
        else:
            if not threads:
                site.get_images(sort=False)
            else:
                site.get_images(threads=int(threads), sort=False)
    if task == '2':
        out = input('csv格式还是json格式？（默认为csv）')
        if out:
            site.get_all_info(out = out)
        else:
            site.get_all_info(out = 'csv')
