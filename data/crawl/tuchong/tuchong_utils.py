import math, requests, threading

def _save_img(url, path):
    with open(path, 'wb') as img:
        img.write(requests.get(url).content)

def _run_threads(n, target):
    t_s = []
    for i in range(n):
        t = threading.Thread(target=target)
        t_s.append(t)
    for t in t_s:
        t.start()
    for t in t_s:
        t.join()

def _suggest_threads(tasks, tasks_per_thread):
    threads = math.ceil(tasks/tasks_per_thread)
    if threads > 10:
        threads = 10
    return threads