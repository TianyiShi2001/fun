from tuchong import Tuchong
import requests
import json
import csv, time, os

def write_time(fp):
    fp.write('#' + time.strftime('%Y-%m-%d') + '\n')

home_url_list = ['https://tuchong.com/' + str(i) + '/posts/' for i in range(2, 10000)]

author_info = []
post_info = []
tag_info = []

for home_url in home_url_list:
    try:
        site = Tuchong(home_url)
        post_info += site.get_post_info()
        author_info.append(site.get_author_info())
        tag_info += site.get_tag_info()
    except:
        print(home_url, '不存在。')



path1 = 'author.csv'

with open(path1, 'w') as fp:
    write_time(fp)
    writer = csv.writer(fp)
    writer.writerow(['user_id', 'username', 'followers'])
    for author in author_info:
        writer.writerow(author)
    print('author数据已写入' + path1)



field = ['post_id', 'author_id', 'published_at', 'image_count', 'favorites', 'comments']

path2 = 'post.csv'

with open(path2, 'w') as fp:
    write_time(fp)
    writer = csv.writer(fp) # write head 
    writer.writerow(field)
    for post in post_info: # every individual is a list
        writer.writerow(post)
    print('post数据已写入' + path2)

path3 = 'tag.csv'

with open(path3, 'w') as fp:
    write_time(fp)
    writer = csv.writer(fp) # write head 
    writer.writerow(['post_id', 'tag'])
    for tag in tag_info: # every individual is a list
        writer.writerow(tag)
    print('tag数据已写入' + path3)
