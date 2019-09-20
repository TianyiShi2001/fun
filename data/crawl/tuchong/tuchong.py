#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "石天熠"

import re, os, csv, json, time, sys, math
import requests
import threading
#import urllib.request


class Tuchong(object):

    def __init__(self, home_url):
        self.home_url = home_url # 如'https://tuchong.com/13044147/posts/'或'tuchong.com/13044147/posts'或'https://asamurai.tuchong.com/posts'
        id = re.findall('\\d+', home_url) # 如'13044147'
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
            j = requests.get('https://tuchong.com/rest/2/sites/' + self.user_id + '/posts?&page=' + str(page_number)).json()
            next_post_list = j['post_list']

            if next_post_list: # 若page_number大于最大页数，j['post_list']将为空
                post_list += next_post_list
            else:
                print('完成。')
                return post_list
            
            page_number += 1
        
    def get_all_info(self, out = 'csv', folder = 'data'):
        self.get_author_info(out = out, folder = folder)
        self.get_post_info(out = out, folder=folder)
        self.get_tag_info(out = out, folder=folder)
        with open(folder + '/post_list.json', 'w') as fp:
            json.dump(self.post_list, fp, ensure_ascii=False)

    def get_author_info(self, out = None, folder = 'data'):
        print('正在提取用户"' + self.username + '"的个人信息...')
        if not os.path.exists(folder + '/'):
            os.mkdir(folder)
        path = folder + '/' + self.user_id + '-author_info'

        author_info = [self.user_id, self.username, self.followers]
        if out is None:
            print('完成。')
            return author_info
        elif out == 'json':
            path += '.json'
            with open(path, 'w') as fp:
                json.dump(author_info, fp)
            print('数据已写入' + path)
        elif out == 'csv':
            path += 'csv'
            with open(path, 'w') as fp:
                writer = csv.writer(fp)
                writer.writerow(['user_id', 'username', 'followers'])
                writer.writerow(author_info)

    def get_post_info(self, out = None, folder = 'data'):
        """从所有原始数据中提取post的信息
        """
        print('正在提取用户"' + self.username + '"的各个post信息...')
        if not os.path.exists(folder + '/'):
            os.mkdir(folder)
        path = folder + '/' + self.user_id + '-post_info'

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
            print('数据已写入' + path)
        elif out == 'csv':
            path += '.csv'
            with open(path, 'w') as fp:
                fp.write('#' + time.strftime('%Y-%m-%d') + '\n')
                writer = csv.writer(fp) # write head 
                writer.writerow(field)
                for individual in post_info: # every individual is a list
                    writer.writerow(individual)
                print('数据已写入' + path)

    def get_tag_info(self, out = None, folder = 'data'):
        """从所有原始数据中提取tag的信息
        """
        print('正在提取用户"' + self.username + '"的各个tag信息...')
        if not os.path.exists(folder + '/'):
            os.mkdir(folder)
        path = folder + '/' + self.user_id + '-tag_info'

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
            print('数据已写入' + path)
        elif out == 'csv':
            path += '.csv'
            with open(path, 'w') as fp:
                fp.write('#' + time.strftime('%Y-%m-%d') + '\n')
                writer = csv.writer(fp)
                writer.writerow(['post_id', 'tag'])
                for instance in tag_info:
                    writer.writerow(instance)
                print('数据已写入' + path)


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
                    image_url = image['source']['lr']
                    this_post_urls.append(image_url)
                id = post["published_at"][0:10] + '-' + post['post_id']
                id_and_image_urls.update({id:this_post_urls})
            print('完成。')
            return id_and_image_urls
        else:
            image_urls = re.findall("'lr': '(.+?)',", str(self.post_list))
            print('完成。')
            return(image_urls)

    def get_images(self, threads = True, sort = True):
        print('正在下载用户"' + self.username + '"的所有图片...')
        if sort:
            # get urls as {time-post_id_1:[url1, url2], time-post_id_2:[url1, url2, ...], ...}
            id_and_urls = self.get_image_urls(sort = True) 
            # initialise parent path
            path = self.user_id + '-' + self.username + '/'
            if not os.path.exists(path):
                os.mkdir(path)

            if threads:
                l = len(id_and_urls)
                if l == 0:
                    raise ValueError('此用户没有发布图片！')
                threads = math.ceil(l/3)
                if threads > 10:
                    threads = 10

            def download_post():
                try:
                     this_post = id_and_urls.popitem()
                except KeyError:
                    sys.exit()
                id, url_s = this_post[0], this_post[1]
                total = len(url_s)
                print('正在下载post', id)
                subdir = path + id + '/'
                if not os.path.exists(subdir):
                    os.mkdir(subdir)
                for i, url in enumerate(url_s, start=1):
                        # urllib.request.urlretrieve(url, subdir + str(i) + '.jpg')
                        with open(subdir + str(i) + '.jpg', 'wb') as img:
                            img.write(requests.get(url).content)
                            print(i, '/', total, ' of post ', id, ' from ', threading.current_thread().name, sep='')
                download_post()
            
            t_s = []
            
            for i in range(threads):
                t = threading.Thread(target=download_post)
                t_s.append(t)
            for t in t_s:
                t.start()
            for t in t_s:
                t.join()
            
            print('完成。')
        else:
            if not os.path.exists('img/'):
                os.mkdir('img/')
            for i, url in enumerate(self.get_image_urls(sort = False)):
                print('正在下载第' + str(i) + '张图片。')
                # urllib.request.urlretrieve(url, 'img/' + self.username + '-' + str(i) + '.jpg')
                with open('img/' + self.username + '-' + str(i) + '.jpg', 'wb') as img:
                    img.write(requests.get(url).content)
            print('完成。')




        

if __name__ == "__main__":
    print('欢迎使用石天熠的图虫信息爬取程序。在命令行使用时，可以用于\n\t（1）下载某个作者的全部图片，或者\n\t（2）获取作者及其全部作品的信息，并以json或csv格式保存。')
    task = input('输入1或者2以继续。')
    home_url = input('请输入作者的主页链接，或者跳过以使用作者（石天熠）的图虫主页链接："https://tuchong.com/13044147/posts/"：')
    if not home_url:
        home_url = 'https://tuchong.com/13044147/posts/'
    site = Tuchong(home_url)

    if task == '1':
        sort = input('是否按照"用户id-用户名/作品id/图片序号.jpg"的结构进行整理？（请输入y或者n）')
        if sort:
            threads = input('你想创建多少个线程用于下载？输入一个数字，或者跳过以自动决定线程数。')
            if not threads:
                site.get_images()
            else:
                site.get_images(threads=threads)
        else:
            site.get_images(sort = False)
    if task == '2':
        out = input('csv格式还是json格式？（默认为csv）')
        if out == 'csv':
            site.get_all_info(out = out)
        elif out == 'json':
            site.get_all_info(out = 'json')
        else:
            site.get_all_info(out = 'csv')
    if task == '3':
        print(site.get_image_urls())