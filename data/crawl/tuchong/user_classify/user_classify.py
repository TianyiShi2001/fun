import requests, csv, threading, sys



# main function

def user_classify():
    global max_, id_s
    global common, special, empty, error
    while id_s:
        i = id_s.pop()
        print(i, '/', max_, ' from ', threading.current_thread().name, sep='')
        try:
            url = 'https://tuchong.com/' + str(i)
            r = requests.get(url, allow_redirects=False, timeout=10)
            if r.status_code == 200:
                common.append(i)
            else:
                r1 = requests.get(url, allow_redirects=True, timeout=10)
                url1 = r1.url 
                if url1 == 'https://tuchong.com/':
                    empty.append(i)
                else:
                    special.append([i, url1])
        except:
            error.append(i)
        user_classify() # iteration 
    else:
        print(threading.current_thread().name, 'Finished!')
        sys.exit()
        return None
    return None



if __name__ == "__main__":

    for x in range(3400000, 6000000, 10000): # 每10000次写入一次数据到硬盘以释放内存

        common = []
        special = []
        empty = []
        error = []

        min_ = x
        max_ = x + 10000

        id_s = list(range(max_, min_, -1))

        # multithreading 

        threads = []

        n_threads = 128

        for i in range(1, 1 + n_threads):
            exec('t{0:s} = threading.Thread(target=user_classify, name="Thread-{0:s}")'.format(str(i)))
            exec('threads.append(t%s)' % i)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # output

        print('OK, now writing to csv.')

        with open('common.csv', 'a') as f:
            for id in common:
                f.write(str(id) + '\n')
        with open('empty.csv', 'a') as f:
            for id in empty:
                f.write(str(id) + '\n')
        with open('special.csv', 'a') as f:
            writer = csv.writer(f)
            for user in special:
                writer.writerow(user)
        with open('error.txt', 'a') as f:
            for id in error:
                f.write(str(id) + '\n')

        print('Finished.')

    print('All finished.')
