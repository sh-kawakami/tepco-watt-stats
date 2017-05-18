#!/usr/bin/env python3

import os
import requests
import argparse
import re
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
csv = session.get(csv_url, headers=csvgetheader)
csv.encoding = csv.apparent_encoding
print(csv.text)
