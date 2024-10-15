import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for

from selenium import webdriver
from selenium.webdriver.common.by import By
import re

djob=[]

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(
            options=options
        )

"""
driver.get("https://baitonet.jp/search/ps_21/")
ahtml = driver.page_source
print("ahtml-1:",ahtml)
"""

#求人件数のページ数を数える関数
def pagecount(html):
      kensu_list = re.findall('検索結果<span class="mainFontColor">(.*)</span>件',html)
      #正規表現でhtmlから求人件数をとってくる
      if kensu_list == []:
        return(1)
        #リストが空なら求人がないから１ページのみ見る
      else:
        kensu_all = kensu_list[0]
        kensu_all_string = kensu_all.replace(',', '')
        #計算をするためにいらない部分を消す
        kensu_all_int = int(kensu_all_string)
        page = kensu_all_int // 20 + 2
        #１ページに２０件の求人票が乗るため、２０で割ってページ数を計算する。あまりの部分もページが必要なので２足す
        return(page)

#求人票のIDを取得する関数
def sagasu(page,name,url):
      job_url_all = []
      #for文で１ページずつ求人票を抽出する
      for i in range(1, page):
        j = str(i)
        URL_job = url + j
        #URLがページ数を含むので入れる
        driver.get(URL_job)
        job_html = driver.page_source
        job_123 = re.findall(name, job_html)
        job_url = list(set(job_123))
        job_url_all = job_url_all + job_url
      return(job_url_all)

#仕事内容の部分の文字数をカウントする関数
def sigotonaiyoucount(job_url_all):
  joblist = []
  for job in job_url_all:
        search_url = 'https://baitonet.jp/' + job
        driver.get(search_url)
        #求人票の詳細ページに飛ぶ
        element = driver.find_element(By.CLASS_NAME, "jobContentsTxt")
        #Webスクレイピングで仕事内容の全体を抽出する
        element = element.text
        elementcount = len(element)
        #文字数をカウントする
        job_only_url = 'https://baitonet.jp/' + job
        jobname = (job.replace('job_', '').replace('/', ''))
        joblist.append([jobname,elementcount,element,job_only_url])
  return(joblist)

def search(number,cur,con):
    p = [1,"北海道", "青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県","埼玉","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]
    todouhuken = str(number)
    todouhuken_url = 'ps_' + todouhuken + '/'
    URL = "https://baitonet.jp/search/" + todouhuken_url
    #print("URL:",URL) 
    driver.get(URL)
    ahtml = driver.page_source
    #print("ahtml:",ahtml)
    apage = pagecount(ahtml)
    #url_sagasu="https://baitonet.jp/search/?page="
    url_sagasu="https://baitonet.jp/search/" + todouhuken_url + "?page="
    jobURL = sagasu(apage,'job_[0-9]{7}/',url_sagasu)
    ajob = sigotonaiyoucount(jobURL)
    
    #jobURL_matome =sagasu(apage,'job_group_[0-9]{3}/',"https://baitonet.jp/search/?page=")
    jobURL_matome =sagasu(apage,'job_group_[0-9]{3}/',"https://baitonet.jp/search/" + todouhuken_url + "?page=")
    bjob = []

    for k in jobURL_matome:
     jobURL_motome_k = 'https://baitonet.jp/' + k +  todouhuken_url
     url_sagasu=jobURL_motome_k+"/?page="
     driver.get(jobURL_motome_k)
     bhtml = driver.page_source
     bpage = pagecount(bhtml)
     if bpage>=2:
        jobURL_b = sagasu(bpage,'job_[0-9]{7}/',url_sagasu)
        bjob = bjob + sigotonaiyoucount(jobURL_b)

    cjob = ajob + bjob
    print("CJOB:",cjob)
    number = int(number)
    for l in cjob:
       cur.execute("insert into numbers (kid,prefecture,count,content) values(?,?,?,?);", (l[0],p[number],l[1],l[2]))

    con.commit()

db = sqlite3.connect(
    'baitonetto.db',
    isolation_level=None,
)

sql = """
    create table if not exists numbers (
      id integer primary key autoincrement,
      kid text not null,
      prefecture text not null,
      count integer,
      content text not null
      )
"""

db.execute(sql)
db.close

table_name = 'numbers'
con = sqlite3.connect('baitonetto.db')
cur = con.cursor()
"""
for i in range(1,47):
    search(i)
"""
search(21,cur,con)
driver.close()
con.close()

