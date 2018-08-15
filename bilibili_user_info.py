# -*-coding:utf8-*-

import requests
import json
import random
import pymysql
import datetime
import time
from multiprocessing import Pool

def getsource(id):

    payload = {
        'mid': '{}'.format(str(id)),
        '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now())
    }

    uas = LoadUserAgents("user_agents.txt")
    ua = random.choice(uas)

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '32',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'UM_distinctid=15b9449b43c1-04dfdd66b40759-51462d15-1fa400-15b9449b43d83; fts=1492841510; sid=j4j61vah; purl_token=bilibili_1492841536; buvid3=30EA0852-5019-462F-B54B-1FA471AC832F28080infoc; rpdid=iwskokplxkdopliqpoxpw; _cnt_pm=0; _cnt_notify=0; _qddaz=QD.cbvorb.47xm5.j1t4z5yc; pgv_pvi=9558976512; pgv_si=s2784223232; _dfcaptcha=02d046fd3cc2bfd2ce6724f8b2185887; CNZZDATA2724999=cnzz_eid%3D1176255236-1492841785-http%253A%252F%252Fspace.bilibili.com%252F%26ntime%3D1492857985',
        'Host': 'space.bilibili.com',
        'Origin': 'http://space.bilibili.com',
        'Referer': 'http://space.bilibili.com/{}/'.format(str(id)),
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
        'User-Agent': ua,
        'X-Requested-With': 'XMLHttpRequest'}

    jscontent = requests.session().post('http://space.bilibili.com/ajax/member/GetInfo', headers=headers, data=payload).text
    # print(jscontent)
    try:
        jsDict = json.loads(jscontent)
        statusJson = jsDict['status'] if 'status' in jsDict.keys() else False
        if statusJson == True:
            if 'data' in jsDict.keys():
                jsData = jsDict['data']

                mid = jsData['mid']
                name = jsData['name']
                sex = jsData['sex']
                face = jsData['face']
                coins = jsData['coins']
                spacesta = jsData['spacesta']
                birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
                place = jsData['place'] if 'place' in jsData.keys() else 'noplace'
                description = jsData['description'] if 'description' in jsData.keys() else 'nodescription'
                article = jsData['article'] if 'article' in jsData.keys() else 0
                playnum = jsData['playNum'] if 'playNum' in jsData.keys() else 0
                sign = jsData['sign']
                level = jsData['level_info']['current_level']
                exp = jsData['level_info']['current_exp'] if 'current_exp' in jsData['level_info'].keys() else '0'

                print("Succeed: " + str(mid) + "\t")
                # print(jsData)
                try:
                    res = requests.get(
                        'https://api.bilibili.com/x/space/navnum?mid=' + str(mid) + '&jsonp=jsonp').text
                    js_data = json.loads(res)
                    video = js_data['data']['video']
                    bangumi = js_data['data']['bangumi']
                except:
                    video = 0
                    bangumi = 0


                user_info = {
                    'mid': mid,
                    'name': name,
                    'sex': sex,
                    'face': face,
                    'coins': coins,
                    'spacesta': spacesta,
                    'birthday': birthday,
                    'place': place,
                    'description': description,
                    'article': article,
                    'video': video,
                    'bangumi': bangumi,
                    'playnum': playnum,
                    'sign': sign,
                    'level': level,
                    'link': 'https://space.bilibili.com/' + str(id),
                    'exp': exp
                }
                print(user_info)
                save_to_mysql(user_info)

            else:
                print('no data now')

        else:
            print("Error: " + str(url))
    except ValueError:
        pass

def datetime_to_timestamp_in_milliseconds(d):
    def current_milli_time(): return int(round(time.time() * 1000))

    return current_milli_time()

def LoadUserAgents(uafile):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1 - 1])
    random.shuffle(uas)
    return uas

def get_id(start, end):
    urls = []
    id = []
    # for m in range(99, 101):  # 26 ,1000
    for i in range(start * 100, end * 100):
        url = 'https://space.bilibili.com/' + str(i)
        urls.append(url)
        id.append(i)
        print(url)
    return id

def create_table(table_name):
    db = pymysql.connect(host='localhost', user='root', password='12041223', port=3306, db='spiders')
    cursor = db.cursor()
    sql = "create table if not exists {table_name}(" \
          "id int(11) unsigned NOT NULL AUTO_INCREMENT primary key," \
          "mid varchar(11) DEFAULT NULL," \
          "name varchar(45) DEFAULT NULL," \
          "sex varchar(11) DEFAULT NULL," \
          "face varchar(200) DEFAULT NULL," \
          "coins int(11) DEFAULT NULL," \
          "spacesta int(11) DEFAULT NULL," \
          "birthday varchar(45) DEFAULT NULL," \
          "place varchar(45) DEFAULT NULL," \
          "description varchar(45) DEFAULT NULL," \
          "article int(11) DEFAULT NULL," \
          "video int(11) DEFAULT NULL," \
          "bangumi int(11) DEFAULT NULL," \
          "playnum int(30) DEFAULT NULL," \
          "sign varchar(300) DEFAULT NULL," \
          "level int(11) DEFAULT NULL," \
          "link varchar(200) DEFAULT NULL," \
          "exp int(11) DEFAULT NULL)".format(table_name = table_name)
    # sql = 'create table if not exists {table_name} (id int auto_increment primary key not null, name varchar(10) not null, age int not null)'.format(table_name = table_name)
    cursor.execute(sql)
    db.close()

def save_to_mysql(data):
    conn = pymysql.connect(
        host='127.0.0.1', port=3306, user='root', passwd='12041223', db='spiders', charset="utf8mb4")
    cursor = conn.cursor()
    table = 'bilibili_user_info'
    keys = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    sql = 'insert into {table}({keys}) values({values})'.format(table = table, keys = keys, values = values)
    try:
        cursor.execute(sql, tuple(data.values()))
        conn.commit()
    except:
        conn.rollback()

    conn.close()


if __name__ == '__main__':
    create_table('bilibili_user_info')
    pool = Pool(1)
    try:
        results = pool.map(getsource, get_id(90, 95))
    except Exception:
        print('ConnectionError')
        pool.close()
        pool.join()
        time.sleep(11)
        pool = Pool(1)
        results = pool.map(getsource, get_id(90, 91))

    # time.sleep(30)

    pool.close()
    pool.join()





