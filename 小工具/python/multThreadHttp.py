import copy
import json
import threading, multiprocessing
import urllib

# import urllib2
from filecmp import cmp

import requests

# 使用 urllib 方式获取
# response = urllib.request.urlopen('http://10.115.25.14/homefeed/v1/vertical?q=新闻&s=0&n=50&t=hfauthor')
# read() 读取的是服务器的原始返回数据 decode() 后会进行转码
# print(response.read().decode())

# 使用 requests 方式获取
# request 模块相比

# url格式需要根据自己定义
urlFormat = "http://www.baidu.com/sug?q=%s"

# 需要重写
def getData(rep) :
    titles = []
    types = []
    hfpos = -1;
    try :
        result = json.loads(rep)
        if ('success' == result['message']):
            data = result['result']
            if (data):
                pos = 0;
                for tmp in data:
                    type = tmp['type']
                    pos += 1
                    if (type):
                        types.append(type)
                        if ("hfauthor" == type):
                            hfdata = tmp["data"]
                            if (hfdata):
                                for tmp2 in hfdata:
                                    title = tmp2["name"]
                                    if (title):
                                        titles.append(title)
                            hfpos = pos
    except Exception as e:
        print(rep)
        print(e)
    return hfpos, titles, types


def handle2 () :
    file = open('/Users/ling.he/Downloads/words20190412094315.txt','r+')
    datafile = open('/Users/ling.he/datafile.txt','w')
    size = 0

    querys = {}
    #先去重统计pv
    for line in file:
        line = line.replace('\n', '')
        querys[line] = querys.get(line, 0) + 1

    print(querys)
    queryResuts = sorted(querys.items(), key = lambda item:item[1], reverse=True)

    size = 0
    for k, v in queryResuts: # 遍历file文件
        size += 1
        resp = requests.post(urlFormat %(k))
        pos, titles, types = getData(resp.text)
        if(pos == -1):
            datafile.write('%s\tfail\n' %(k))
        else:
            datafile.write('%s\tsuccess\t%d\t%s\t%s\t%d\n' %(k, pos, titles, types, v))
        print(size)


    file.close()# 关闭文件
    datafile.close()


def handle() :
    file = open('/Users/ling.he/Downloads/words20190412094315.txt','r+')
    datafile = open('/Users/ling.he/datafile.txt','w')
    size = 0
    for line in file: # 遍历file文件
        size += 1
        line = line.replace('\n', '')
        resp = requests.post(urlFormat %(line))
        pos, titles, types = getData(resp.text)
        if(pos == -1):
            datafile.write('%s\tfail\n' %(line))
        else:
            datafile.write('%s\tsuccess\t%d\t%s\t%s\n' %(line, pos, titles, types))
        #print('%s\tsuccess\t%d\t%s\t%s\n' %(line, pos, titles, types))
        print(size)


    file.close()# 关闭文件
    datafile.close()

def test() :
    resp = requests.post(urlFormat %('虎扑'))
    print(resp.text)
    pos, titles, types = getData(resp.text)
    print(pos)
    print(titles)
    print(types)

#################################

# MyThread.py线程类
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None




def list_of_groups(init_list, childern_list_len):
    '''
    init_list为初始化的列表，childern_list_len初始化列表中的几个数据组成一个小列表
    :param init_list:
    :param childern_list_len:
    :return:
    '''
    list_of_group = zip(*(iter(init_list),) *childern_list_len)
    end_list = [list(i) for i in list_of_group]
    count = len(init_list) % childern_list_len
    end_list.append(init_list[-count:]) if count !=0 else end_list
    return end_list

def mitilhandle () :
    file = open('/Users/ling.he/Downloads/words20190412121628.txt','r+')
    datafile = open('/Users/ling.he/nothotdatafile.txt','w')
    size = 0

    querys = {}
    #先去重统计pv
    for line in file:
        line = line.replace('\n', '')
        querys[line] = querys.get(line, 0) + 1

    print(querys)
    queryResuts = sorted(querys.items(), key = lambda item:item[1], reverse=True)

    pvm = 0
    for k, v in queryResuts:  # 遍历file文件
        if (v > 1):
            pvm += 1
    print(pvm)

    mutipQuerys = list_of_groups(queryResuts, 4000)

    theendreutl = []

    nloops = 0
    threads = []
    for queryssplit in mutipQuerys:
        t = MyThread(onethred, (queryssplit,nloops,))
        threads.append(t)
        nloops += 1

    for i in range(nloops):  # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
        threads[i].start()

    for i in range(nloops):  # jion()方法等待线程完成
        threads[i].join()

    for i in range(nloops):  # jion()方法等待线程完成
        theendreutl.append(threads[i].get_result())

    size = 0
    for values in theendreutl: # 遍历file文件
        if (values):
            for tm in values:
                size += 1
                datafile.write(tm)
                print("end size :%d" %(size))


    file.close()
    datafile.close()

def onethred(queryResuts, num):
    result = []
    size = 0
    for k, v in queryResuts:  # 遍历file文件
        size += 1
        try :
            resp = requests.post(urlFormat % (k))
            pos, titles, types = getData(resp.text)
            if (pos == -1):
                # result.append('%s\t\t%d\n' % (k,v))
                result.append('%s\tnone\t%d\t%d\t%s\t%s\n' % (k, v, pos, titles, types))
            else:
                result.append('%s\tsuccess\t%d\t%d\t%s\t%s\n' % (k, v, pos, titles, types))
        except:
            print(k,v)
            result.append('%s\tfail\t%d\n' % (k, v))

    print("thread %d, size %d" %(num, size))
    return result



mitilhandle()
