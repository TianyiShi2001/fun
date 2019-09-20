import requests, threading, csv, sys, os

os.system('Rscript retry.R')

def user_reclassify(): # dealing with error ids
    global common, special, empty, error, error_new
    while error:
        i = error.pop()
        print(i, ' from ', threading.current_thread().name, sep='')
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
            error_new.append(i)
        user_reclassify() # iteration 
    else:
        print(threading.current_thread().name, 'Finished!')
        sys.exit()
        return None
    return None

if __name__ == "__main__":

    with open('error.txt') as f:
        error = f.read().splitlines()

    error_new = []

    common = []
    special = []
    empty = []

    # multithreading

    threads = []

    n_threads = 1

    for i in range(1, 1 + n_threads):
        exec('t{0:s} = threading.Thread(target=user_reclassify, name="Thread-{0:s}")'.format(str(i)))
        exec('threads.append(t%s)' % i)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # output

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
    with open('error_real.txt', 'a') as f:
        for id in error_new:
            f.write(str(id) + '\n')
    with open('error.txt', 'w') as f:
        f.write('')