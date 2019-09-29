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
        self.get_author_info(out = out)
        self.get_tag_info(out = out)
        self.get_tag_wordcloud()
        with open(path + 'post_list.json', 'w') as fp:
            json.dump(self.post_list, fp, ensure_ascii=False)

    def get_author_info(self, out = None):
        print('正在提取与"' + self.query + '"相关的图片的所有作者的信息...')
        path = self._mkdir('data')
        path += 'author_info'

        author_info = []
        added_id = []
        field = ['user_id', 'username', 'followers']
        for post in self.post_list:
            if post['author_id'] not in added_id:
                author_info.append({
                    field[0]:post['author_id'],
                    field[1]:post['site']['name'],
                    field[2]:post['site']['followers']
                })
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
                writer = csv.DictWriter(fp, fieldnames = field)
                writer.writerows(author_info)

    def get_post_info(self, out = None):
        """从所有原始数据中提取post的信息
        """
        print('正在提取与"' + self.query + '"相关的所有posts的信息...')
        path = self._mkdir('data')
        path += 'post_info'

        post_info = [] # a list containing dicts of individual post info
        field = ['author_id', 'post_id', 'title', 'excerpt', 'published_at', 'image_count', 'favorites', 'comments']
        for post in self.post_list:
            new_post_info = {} # every individual is a dict
            for key in field:
                new_post_info.update({key:post[key]})
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
                writer = csv.DictWriter(fp, fieldnames = field)
                writer.writeheader() # write head
                writer.writerows(post_info)
        print('数据已写入' + path)

    def get_tag_info(self, out = None):
        """从所有原始数据中提取tag的信息
        """
        print('正在提取与"' + self.query + '"相关的图片的tag信息...')
        path = self._mkdir('data')
        path += 'tag_info'

        tag_info = []
        for post in self.post_list:
            tag_info.append({'post_id':post['post_id'], 'tags':list(map(lambda t: t['tag_name'], post['tags']))}) 
        if out is None:
            return tag_info
        elif out == 'json':
            path += '.json'
            with open(path, 'w') as fp:
                json.dump(tag_info, fp)
        elif out == 'csv':
            path += '.csv'
            tag_info = []
            for post in self.post_list:
                for tag in post['tags']:
                    tag_info.append([post['post_id'], tag['tag_name']]) # append instances in the form of [post_id, tag_name]
            with open(path, 'w') as fp:
                fp.write('#' + time.strftime('%Y-%m-%d') + '\n')
                writer = csv.writer(fp)
                writer.writerow(['post_id', 'tag'])
                for instance in tag_info:
                    writer.writerow(instance)
        print('数据已写入' + path)

    def get_tag_wordcloud(self):
        print('正在生成词云...')
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
    
    def get_image_urls(self, sort = True, min_fav = None):
        print('正在提取与"' + self.query + '"相关的所有图片链接...')
        post_list = self.post_list
        if min_fav:
            post_list = list(filter(lambda post:post['favorites']>=min_fav, self.post_list))
        if sort:
            id_and_image_urls = {}
            for post in post_list:
                this_post_urls = [] # each post can have multiple images
                for image in post['images']: # looping over the list of images of this post
                    image_url = image['source']['lr'] # e.g. https://tuchong.pstatp.com/33937/lr/397648555.jpg
                    image_url = re.sub('/lr/', '/f/', image_url) # convert to 'full' size
                    this_post_urls.append(image_url)
                id = str(post['favorites']) + '-' + post['site']['name'] + '-' + '-' + post['post_id'] + post["published_at"][0:10] # 获赞数放在前面
                id_and_image_urls.update({id:this_post_urls})
            print('完成。')
            return id_and_image_urls
        else:
            image_urls = re.findall("'lr': '(.+?)',", str(post_list))
            image_urls = list(map(lambda image_url:re.sub('/lr/', '/f/', image_url), image_urls))
            print('完成。')
            return image_urls

    def get_images(self, min_fav = None, threads = 'auto', sort = True, txt = True):
        path = self._mkdir('img')

        if sort:
            id_and_urls = self.get_image_urls(sort = True, min_fav = min_fav)
            if isinstance(threads, int):
                threads = threads
            else:
                threads = _suggest_threads(len(id_and_urls), 3)
            def download_post(path = path):
                nonlocal id_and_urls
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
                # txt_path = path + id + '.txt'
                for i, url in enumerate(url_s, start=1):
                    img_path = path + str(i) + '.jpg'
                    _save_img(url, img_path)
                    print(i, '/', total, ' of post ', id, ' from ', threading.current_thread().name, sep='')
                    # with open()
                download_post() # 递归
            # 多线程
            _run_threads(n = threads, target=download_post)
        else: # 如果不需要整理
            image_urls = self.get_image_urls(sort = False, min_fav = min_fav)

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

class TuchongTag(TuchongQuery):

    def __init__(self, tagQuery, order = 'weekly'):
        self.query = tagQuery
        self.post_list = self.get_post_list_raw(order)

    def get_post_list_raw(self, order):
        print('正在抓取带有"' + self.query + '"标签的所有作品的源信息...')

        pages = list(range(100, 0, -1))

        post_list = []

        lock = threading.Lock()

        def page(order = order):
            nonlocal post_list, pages
            try:
                page_number = pages.pop()
            except IndexError:
                sys.exit()

            url = 'https://tuchong.com/rest/tags/' + self.query + '/posts?count=100&page=' + str(page_number) + '&order=' + order # e.g. https://tuchong.com/rest/search/posts?query=JK+少女&page=1&order=weekly, count 为每页posts数量
            j = requests.get(url).json()
            try:
                next_post_list = j['postList']
            except:
                sys.exit()
            lock.acquire() # 防止两个线程同时访问公有变量
            post_list += next_post_list
            lock.release()
            print('完成第', page_number, '页', sep='')
            page(order=order)

        _run_threads(10, target=page)

        return post_list

    def get_all_info(self, out = 'csv'):
        path = self._mkdir('data')
        self.get_post_info(out = out)
        self.get_tag_info(out = out)
        self.get_tag_wordcloud()
        with open(path + 'post_list.json', 'w') as fp:
            json.dump(self.post_list, fp, ensure_ascii=False)

    def get_author_info(self, out = None):
        pass
        print('正在提取与"' + self.query + '"相关的图片的所有作者的信息...')
        import pickle
        path = self._mkdir('data')
        path += 'author_info'

        author_info = []
        added_id = []
        field = ['user_id', 'username', 'followers']
        with open('cache/author', 'rb') as f:
            cache = pickle.load(f)
        for post in self.post_list:
            author_id = post['author_id']
            if  author_id not in added_id and author_id not in cache:
                html = requests.get('https://tuchong.com/' + author_id).text
                followers = re.findall(r'粉丝 (\d+)', html)
                import lxml.etree as le
                username = ''.join(le.HTML(html).xpath('//div[@class="title"]//text()')).strip()
                author_info.append({
                    field[0]:author_id,
                    field[1]:post['site']['name'],
                    field[2]:followers
                })

        
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
                writer = csv.DictWriter(fp, fieldnames = field)
                writer.writerows(author_info)

    def get_tag_wordcloud(self):
        print('正在生成词云...')
        path = self._mkdir('data')
        path += 'wordcloud.jpg'

        tag_s = []
        for post in self.post_list:
            for tag in post['tags']:
                t = tag['tag_name']
                if t.lower() != self.query: # 否则query对应的字符就会很大
                    tag_s.append(t)
        
        txt = ' '.join(tag_s)

        cloud = WordCloud(font_path='SourceHanSerifCN-Light.otf',
                          background_color='white',
                          margin=5, width=1920, height=1080)
        
        cloud.generate(txt).to_file(path)
        print('词云已写入' + path)

    def get_image_urls(self, sort = True, min_fav = None):
        print('正在提取与"' + self.query + '"相关的所有图片链接...')
        post_list = self.post_list
        if min_fav:
            post_list = list(filter(lambda post:post['favorites']>=min_fav, self.post_list))
        if sort:
            id_and_image_urls = {}
            for post in post_list:
                this_post_urls = [] # each post can have multiple images
                for image in post['images']: # looping over the list of images of this post
                    image_id = image['img_id_str'] 
                    image_url = 'https://tuchong.pstatp.com/' + post['author_id'] + '/lr/' + image_id + '.jpg' # e.g. https://tuchong.pstatp.com/33937/lr/397648555.jpg
                    this_post_urls.append(image_url)
                id = str(post['favorites']) + '-' + post['author_id'] + '-' + post['post_id'] + '-' + post["published_at"][0:10] # 获赞数放在前面
                id_and_image_urls.update({id:this_post_urls})
            print('完成。')
            return id_and_image_urls
        else:
            pass
            image_urls = re.findall("'lr': '(.+?)',", str(post_list))
            image_urls = list(map(lambda image_url:re.sub('/lr/', '/f/', image_url), image_urls))
            print('完成。')
            return image_urls

    def get_html(self, min_fav = None):
        id_and_urls = self.get_image_urls(min_fav = min_fav)
        path = self._mkdir('img')
        path += 'ranked.html'
        HTML = '<head>\n\t<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">\n<meta charset="utf-8">\n</head>\n<body>\n<div class="container">\n'
        for id in sorted(id_and_urls.keys(), key=lambda id: int(str(id).split('-', 3)[0]), reverse=True):
            url_s = id_and_urls[id]
            fav, author_id, post_id, time = id.split('-', maxsplit=3)
            URL = 'https://tuchong.com/' + author_id + '/' + post_id
            new = f'\t<h2>获赞：{fav}  时间：{time}</h2>\n\t<h3><a href="{URL}">源链接</a></h3>\n'
            for url in url_s:
                new += f'\t\t<img class="img-fluid" src="{url}">\n'
            HTML += new
        HTML += '<div>\n</body>'
        with open(path, 'w') as fp:
            fp.write(HTML)

    
    
if __name__ == "__main__":
    q = input('你想搜索的标签是？')
    t = TuchongTag(q, 'weekly')
    # t.get_all_info()
    t.get_html(min_fav=100)