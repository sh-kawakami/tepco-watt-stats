#!/usr/bin/env python3

import os
import requests
import argparse
import re
import csv
import io
import json
from datetime import date
from pprint import pprint
from urllib.parse import quote

# 引数処理
parser = argparse.ArgumentParser()
parser.add_argument(
    'date', help="使用量を取得したい日付(YYYY-MM-DD もしくは YYYY-MM もしくは YYYY)")
parser.add_argument('-j', '--json', help="JSON 形式で出力", action="store_true")
args = parser.parse_args()

# 引数で渡された日付を処理
ymd = args.date.split('-')
year = date.today().timetuple()[0]
month = None
day = None
if(re.match('^[0-9]{4}$', ymd[0])):
    year = int(ymd[0])
if(len(ymd) >= 2 and re.match('^[0-9]{2}$', ymd[1]) and int(ymd[1]) <= 12):
    month = int(ymd[1])
if(len(ymd) >= 3 and re.match('^[0-9]{2}$', ymd[2]) and int(ymd[2]) <= 31):
    day = int(ymd[2])

# ログイン情報設定
username = os.environ['TEPCO_WATT_USERNAME']
password = os.environ['TEPCO_WATT_PASSWORD']

session = requests.Session()

# ログイン 念のため一度トップページへアクセスして cookie を食べる
loginparam = {
    'ACCOUNTUID': username,
    'PASSWORD': password,
    'HIDEURL': '/pf/ja/pc/mypage/home/index.page?',
    'LOGIN': 'EUAS_LOGIN',
}
loginheader = {
    'Referer': 'https://www.kurashi.tepco.co.jp/kpf-login',
    'Content-Type': 'application/x-www-form-urlencoded',
}
session.get('https://www.kurashi.tepco.co.jp/kpf-login')
login = session.post(
    'https://www.kurashi.tepco.co.jp/kpf-login', data=loginparam, headers=loginheader,)

# CSV 取得前に使用量ページの cookie を食べておく必要があるようなのでリクエストを投げる
session.get(
    'https://www.kurashi.tepco.co.jp/pf/ja/pc/mypage/learn/comparison.page')

# URL を組み立てて CSV データを取ってくる
csv_url = 'https://www.kurashi.tepco.co.jp/pf/ja/pc/mypage/learn/comparison.page?ReqID=CsvDL&year=' + \
    str(year)
if(month != None and day != None):
    csv_url = '%s&month=%00d&day=%00d' % (csv_url, month, day)
elif(month != None):
    csv_url = '%s&month=%00d' % (csv_url, month)

csvgetheader = {
    'Referer': 'https://www.kurashi.tepco.co.jp/pf/ja/pc/mypage/learn/comparison.page',
}
csvdata = session.get(csv_url, headers=csvgetheader)
csvdata.encoding = csvdata.apparent_encoding

# -j/--json オプションがあれば JSON に仕立てて表示、無ければ生データを表示
if(args.json == True):
    lines = csv.reader(io.StringIO(initial_value=csvdata.text))

    stats = {
        'お客さま番号': "",
        '事業所コード': "",
        'ご請求番号': "",
        '供給地点特定番号': "",
        '使用量': []
    }

    for line in lines:
        if (line[7] == '契約メニュー'):
            continue
        if (line[5] == '契約メニュー' and not month and not day):
            continue

        stats['お客さま番号'] = line[0]
        stats['事業所コード'] = line[1]
        stats['ご請求番号'] = line[2]
        stats['供給地点特定番号'] = line[3]
        if (month):
            dow_idx = 5
            menu_idx = 7
            usage_idx = 8
            sell_idx = 9
        else:
            # year only mode
            dow_idx = -1
            menu_idx = 5
            usage_idx = 9
            sell_idx = 23
        usage = 0.0 if line[usage_idx] == '' else float(line[usage_idx])
        sell = 0.0 if line[sell_idx] == '' else float(line[sell_idx])
        d = {'年月日': line[4]}
        if (month):
            d.update({
                '曜日': line[dow_idx],
                '休祝日': True if line[6] == "○"  else False})
        d.update({
            '契約メニュー': line[menu_idx],
            'ご使用量': usage,
            '売電量': sell,
        })
        stats['使用量'].append(d)

    print(json.dumps(stats, ensure_ascii=False))
else:
    print(csvdata.text)
