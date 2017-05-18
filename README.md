# tepco-watt-stats

くらしTEPCO(https://www.kurashi.tepco.co.jp/pf/ja/pc/mypage/home/index.page )のページから、電力使用量のデータを取得するスクリプトです。

# Usage

あらかじめ、ログイン用ユーザIDとパスワードの値を、それぞれ環境変数 TEPCO_WATT_USERNAME と TEPCO_WATT_PASSWORD にセットしておいてください。

```
python3 tepco-watt-stats.py YYYY-MM-DD
python3 tepco-watt-stats.py YYYY-MM
python3 tepco-watt-stats.py YYYY
```

引数に渡す日付が
+ 年のみの場合は、その年の月単位の使用量データを
+ 年と月の場合は、その月の日単位の使用量データを
+ 年と月と日の場合は、その日の時間単位(30分刻み)の使用量データを

それぞれ取得します。

なお現状は、CSV データをそのまま標準出力に出力するだけです。他の形式での出力は追々実装予定。
