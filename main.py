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
    browser = p.chromium.launch(headless=True, channel="chrome")
    page = browser.new_page()

    # 登录
    page.goto("https://onecas.cau.edu.cn/tpass/login")
    page.fill("#un", username)
    page.fill("#pd", password)
    page.click("#index_login_btn")

    page.goto("https://one.cau.edu.cn/tp_up/view?m=up#act=up/pim/allpim")

    page.wait_for_selector("div.tz-body-list")

    news_list: list[News] = []
    
    items = page.locator("div.tz-body-list").all()
    
    for item in items:
        title = item.locator("a.tit").inner_text()
        
        date = item.locator("p.pull-right-to-left span").last.inner_text()
        
        news_list.append(News(
            title=title.strip(),
            date=date.strip()
        ))
    news_list.sort(key=lambda x: x.date, reverse=True)
    for news in news_list:
        print(f"日期: {news.date} | 标题: {news.title}")

    html_template = Template("""
        <h3>校内最新通知</h3>
        <ul>
            {% for news in news_list %}
            <li>[{{ news.date }}] {{ news.title }}</li>
            {% endfor %}
        </ul>
    """)
    email_body = html_template.render(news_list=news_list)

    resend.Emails.send({
        "from": sender_email,
        "to": receiver_email,
        "subject": f"校内新闻更新 - {len(news_list)}条",
        "html": email_body,
    })
    browser.close()