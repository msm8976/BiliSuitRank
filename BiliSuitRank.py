import time
import threading
import random
import os
import sys
from xdaili import getbyproxy

# 模式 用以设置延时参数及uid转换数量
mode = 1

# timels(s) delayls(ms) num(int)
# 你也可以新建延时参数模式或修改预设的参数
if mode == 0:
    timels = [15, 120, 300, 600, 1800]
    delayls = [(80, 120), (120, 180), (200, 300), (300, 500), (500, 1000)]
    num = 200
elif mode == 1:
    timels = [10, 15, 30, 60, 180]
    delayls = [(80, 120), (200, 300), (500, 800), (1000, 2000), (3000, 5000)]
    num = 120
elif mode == 2:
    timels = [5, 8, 15, 30, 60]
    delayls = [(80, 120), (120, 180), (240, 360), (600, 1000), (2000, 3000)]
    num = 100
elif mode == 3:
    timels = [5, 8, 15]
    delayls = [(80, 120), (120, 180), (300, 500)]
    num = 80
elif mode == 8976:#不进行用户名uid转换 长时间爬取
    timels = [0, 89768976]
    delayls = [(8976, 8976), (5000, 8000)]
    num = 0
else:#仅进行本地文件的用户名uid转换
    timels = [0]
    delayls = [(8976, 8976)]
    num = mode

totalnum = 0
successnum = 0
datalssize = 32
datals = [[] for i in range(datalssize)]


def getrank():
    if len(timels) != len(delayls):
        print('延时参数错误，请检查')
        return
    item_id, item_time = gettime()
    if time.time() > item_time:
        print('装扮已开售')
    url = 'http://api.bilibili.com/x/garb/rank/fan/recent?item_id=' + item_id
    while time.time() < item_time - 3.2:
        time.sleep(3)
    print('准备开始获取')
    while time.time() < item_time:
        time.sleep(0.2)
    print('开始获取\t' + str(time.time()))

    try:
        for i in range(len(timels)):
            delaymin, delaymax = delayls[i]
            while time.time() < item_time + timels[i]:
                saverank_thread = threading.Thread(target=saverank, args=(url,), daemon=True)
                saverank_thread.start()
                time.sleep(random.randint(delaymin, delaymax)/1000)
            if i == 1:
                name2uid_thread = threading.Thread(target=name2uid, args=(num,))
                name2uid_thread.start()
    except:
        print('停止运行')
    print('获取完成\t总共' + str(totalnum) + '次\t成功' + str(successnum) + '次')
    mergefile()
    return


def gettime():
    item_time = 0
    itemurl = 'http://api.bilibili.com/x/garb/mall/item/suit/v2?item_id='
    item_id = input('请输入装扮id\n')
    while item_time == 0:
        try:
            item_detail = getbyproxy(itemurl + item_id).json()['data']['item']
        except KeyboardInterrupt:
            sys.exit()
        except BaseException:
            print('获取装扮信息失败，即将重试')
            time.sleep(1)
        else:
            if item_detail['item_id'] != 0:
                item_name = item_detail['name']
                item_time = int(item_detail['properties']['sale_time_begin'])
            else:
                print('装扮id错误，请检查')
                sys.exit()
    print('装扮名称\t' + item_name)
    print('开售时间\t' + time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime(item_time)))
    if os.path.exists(item_id + '-' + item_name) == False:
        os.mkdir(item_id + '-' + item_name)
    os.chdir(item_id + '-' + item_name)
    return item_id, item_time


def saverank(url):
    global totalnum
    global successnum
    totalnum += 1
    currentnum = totalnum
    try:
        response = getbyproxy(url)
    except:
        print(str(currentnum) + '线程获取失败')
    else:
        try:
            rankls = response.json()['data']['rank']
            if len(rankls):
                rankls.reverse()
                datals[currentnum % datalssize] = rankls.copy()
                with open(str(datals[currentnum % datalssize][0]['number']) + '-' + str(datals[currentnum % datalssize][-1]['number']) +
                          time.strftime('-%H-%M-%S-', time.localtime(time.time())) + str(time.time() - int(time.time()))[2:8] + '.txt', 'w', encoding='utf-8') as file:
                    for rank in datals[currentnum % datalssize]:
                        file.write('{0:<6}\t{1}\n'.format(str(rank['number']), rank['nickname']))
                print(str(currentnum) + '线程获取成功 ' + str(datals[currentnum % datalssize][-1]['number']))
                successnum += 1
            else:
                print(str(currentnum) + '线程数据为空')
        except Exception as e:
            print(str(currentnum) + '线程解析失败 ' + str(e))


def name2uid(num=100):
    print('开始进行用户名uid转换')
    starttime = time.time()
    infols = []
    url = 'https://api.vc.bilibili.com/dynamic_mix/v1/dynamic_mix/name_to_uid?names='
    filepath = os.getcwd()
    filelist = list(filter(lambda x: list(x.split('-'))[0].isdigit() , os.listdir()))
    filelist.sort(key=lambda f: int(list(f.split('-'))[0]))
    for filename in filelist:
        try:
            if int(list(filename.split('-'))[0]) > num:
                break
            with open(os.path.join(filepath, filename), encoding='utf-8', buffering=1) as file:
                for line in file:
                    number, name = line[0:-1].split('\t')
                    number = number.replace(' ', '')
                    if number == 'number':
                        continue
                    if int(number) > num + 50:
                        print(filename + '文件信息异常')
                        break
                    infols.append((number, name))
        except:
            print(filename + '读取错误')
            continue
    infols = sorted(list(set(infols)), key=lambda x: int(x[0]))
    with open('name2uid_' + str(num) + time.strftime('_%H-%M-%S-', time.localtime(time.time())) + str(time.time()-int(time.time()))[2:8] + '.txt', 'a', encoding='utf-8') as file:
        file.write('{0:<6}\t{1:<9}\t{2}\n'.format('number', 'uid', 'nickname'))
        print(infols)
        needexit = 0
        for info in infols:
            success = 0
            number, name = info
            while not success:
                try:
                    response = getbyproxy(url + name)
                    data = response.json()['data']
                    if len(data) == 1:
                        uid = 'null'
                    else:
                        uid = data['uid_list'][0]['uid']
                    result = '{0:<6}\t{1:<9}\t{2}'.format(number, uid, name)
                    success = 1
                except KeyboardInterrupt:
                    needexit = 1
                    success = 1
                except BaseException:
                    print(number + '失败')
                    time.sleep(0.2)
            if needexit:
                break
            print(result)
            file.write(result + '\n')
    print('转换uid完成，耗时' + str(int(time.time() - starttime)) + '秒')


def mergefile():
    infols = []
    filepath = os.getcwd()
    filelist = list(filter(lambda x: list(x.split('-'))[0].isdigit() , os.listdir()))
    for filename in filelist:
        try:
            with open(os.path.join(filepath, filename), encoding='utf-8', buffering=1) as file:
                for line in file:
                    number, name = line[0:-1].split('\t')
                    number = number.replace(' ', '')
                    if number == 'number':
                        continue
                    infols.append((number, name))
        except:
            print(filename + '读取错误')
            continue
    infols = sorted(list(set(infols)), key=lambda x: int(x[0]))
    with open('merge_' + str(len(infols)) + time.strftime('_%H-%M-%S-', time.localtime(time.time())) + str(time.time() - int(time.time()))[2:8] + '.txt', 'a', encoding='utf-8') as file:
        file.write('{0:<6}\t{1}\n'.format('number', 'nickname'))
        for info in infols:
            file.write('{0:<6}\t{1}\n'.format(info[0], info[1]))
    print('合并完成')


def test():
    if os.path.exists('test') == False:
        os.mkdir('test')
    starttime = time.time()
    response = getbyproxy('http://api.bilibili.com/x/garb/rank/fan/recent?item_id=32296')
    endtime = time.time()
    print('延迟' + str(int(1000*(endtime - starttime))) + 'ms')
    print(response.text[-20:])
    try:
        rankls = response.json()['data']['rank']
        with open('test/test-' + str(rankls[0]['number']) + '-' + str(rankls[-1]['number']) + time.strftime('-%H-%M-%S-',
                  time.localtime(time.time())) + str(time.time() - int(time.time()))[2:8] + '.txt', 'w', encoding='utf-8') as file:
            file.write('延迟 ' + str(int(1000*(endtime - starttime))) + 'ms\n')
            for rank in rankls:
                file.write('{0:<6}\t{1}\n'.format(str(rank['number']), rank['nickname']))
    except Exception as e:
        print('解析失败 ' + str(e))
        print(response.text)


if __name__ == '__main__':
    test()
    getrank()
