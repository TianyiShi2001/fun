import requests

'''
bad login
General
    Request URL: https://tuchong.com/rest/accounts/login
    Request Method: POST
    Status Code: 200 OK
    Remote Address: 123.58.9.84:443
    Referrer Policy: no-referrer-when-downgrade
Request Headers
    Connection: keep-alive
    Content-Length: 297
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    Cookie: PHPSESSID=a7asht3p6i99qi78si5s5d89r0; _ga=GA1.2.1139566251.1541969897; log_web_id=5030076977; lang=zh; __utmc=115147160; __utmz=115147160.1567693864.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); wluuid=WLGEUST-5B927A38-C010-33F7-DFF8-AC1F72E0196C; wlsource=tc_pc_home; ssoflag=0; _gid=GA1.2.42106200.1568638113; weilisessionid3=c4a79d1826802c53aa7983a82f2654a8; webp_enabled=1; email=shitianyi2001%40outlook.com; __utma=115147160.1139566251.1541969897.1568771888.1568950060.5; _gat=1
    Host: tuchong.com
    Origin: https://tuchong.com
    Referer: https://tuchong.com/community
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36
    X-Requested-With: XMLHttpRequest
Form Data
    account=18765438765&password=18752e2b9714f5e709b3405c070bb42952078bf83828b3bbd27dfe324505a6d935d7050e9fa0cc820f9824ae59c524c478775029eb7bdd3ff4b0bd9296bcbf413c6975ae2ff10d2838a22bcb79fb1f04f130c3b5fd81116f9e44ee5234c8b9c5d1be29023ae3711b54af83a8f3aeea99b4e892a5907db5c0a7bff67ec24ae0c1&remember=on
'''

userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'

headers = {
    # "origin": "https://passport.mafengwo.cn",
    "Referer": "https://passport.mafengwo.cn/",
    'User-Agent': userAgent,
}

def tuchong_login(account, password):
    print('开始模拟登陆图虫网（tuchong.com)...')
    
    post_url = 'https://tuchong.com/rest/accounts/login'
    post_data = {
        'passport': account,
        'password': password
    }
    response_res = requests.post(post_url, data=post_data, headers=headers)
    # 无论是否登录成功，状态码一般都是 status_code = 200
    print(f'status_code = {response_res.status_code}')
    print(f'text = {response_res.text}')

if __name__ == "__main__":
    tuchong_login('18676438253', '123qazpl,')


'77f0ad15312e813ebccf6216913f4d42bd5b5008c16cac2b2179575b19d962f0e769719e944bb560b71d8864be8e26db92372dabc7975d52933938008f56e6e5f1edfdff2810baec1bfec357af72941eabe91c4d0bc98ff69c7765123b9761dfed65333f8329980eea0356b05dd0e3708b282b4faf34ad96ad25bac3404eb204'


https://static.tuchong.net/js/rsa.min.js

