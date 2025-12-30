import os
from playwright.sync_api import sync_playwright
from dataclasses import dataclass
from jinja2 import Template
import resend

@dataclass
class News:
    title: str
    date: str

sender_email = "news@mail.sanbei101.cn"
receiver_email = "1317627853@qq.com"
username = os.environ["CAU_USERNAME"]                                                                                           
password = os.environ["CAU_PASSWORD"]                                                                                           
resend.api_key = os.environ["RESEND_API_KEY"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 登录
    page.goto("https://onecas.cau.edu.cn/tpass/login")
    page.fill("#un", username)
    page.fill("#pd", password)
    page.click("#index_login_btn")


    print("正在抓取校级通知...")
    page.goto("https://one.cau.edu.cn/tp_up/view?m=up#act=up/pim/allpim")
    page.wait_for_selector("div.tz-body-list")
    news_list: list[News] = []
    ciee_news_list : list[News] = []
    items = page.locator("div.tz-body-list").all()
    for item in items:
        title = item.locator("a.tit").inner_text()
        date = item.locator("p.pull-right-to-left span").last.inner_text()
        news_list.append(News(
            title=title.strip(),
            date=date.strip()
        ))

    print("正在抓取信电学院通知...")
    page.goto("https://ciee.cau.edu.cn/col/col50390/")
    page.wait_for_selector(".list_box_list")
    ciee_items = page.locator("ul.list_box_list div.default_pgContainer li").all()
    for item in ciee_items:
        title = item.locator("h5.overfloat-dot").inner_text().strip()
        ym = item.locator(".time h6").inner_text().strip()
        day = item.locator(".time h3").inner_text().strip().zfill(2)
        full_date = f"{ym}-{day}"
        ciee_news_list.append(News(title=title, date=full_date))
    
    news_list.sort(key=lambda x: x.date, reverse=True)
    ciee_news_list.sort(key=lambda x: x.date, reverse=True)
    for news in news_list:
        print(f"学校通知: 日期: {news.date} | 标题: {news.title}")
    for news in ciee_news_list:
        print(f"信电通知: 日期: {news.date} | 标题: {news.title}")
    html_template = Template("""
        <h3>校内最新通知</h3>
        <ul>
            {% for news in news_list %}
            <li>[{{ news.date }}] {{ news.title }}</li>
            {% endfor %}
        </ul>
        <h3>信电学院最新通知</h3>
        <ul>
            {% for news in ciee_news_list %}
            <li>[{{ news.date }}] {{ news.title }}</li>
            {% endfor %}
        </ul>
    """)
    email_body = html_template.render(news_list=news_list, ciee_news_list=ciee_news_list)

    resend.Emails.send({
        "from": sender_email,
        "to": receiver_email,
        "subject": f"校内新闻更新 - {len(news_list)}条",
        "html": email_body,
    })
    browser.close()