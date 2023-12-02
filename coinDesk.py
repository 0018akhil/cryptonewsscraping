import json
import scrapy
import random
from bs4 import BeautifulSoup
import pymongo
from deep_translator import GoogleTranslator

def lang_trans(content_obj):

    output = {}
    translator_german = GoogleTranslator(source='english', target='german')
    translator_japanese = GoogleTranslator(source='english', target='japanese')
    translator_italian = GoogleTranslator(source='english', target='italian')
    translator_portuguese = GoogleTranslator(source='english', target='portuguese')
    translator_french = GoogleTranslator(source='english', target='french')
    translator_spanish = GoogleTranslator(source='english', target='spanish')

    main_transulator = {"DE":translator_german, "JP":translator_japanese, "IT":translator_italian, "PT":translator_portuguese, "FR":translator_french, "ES":translator_spanish}

    for key in main_transulator:
        headline = main_transulator[key].translate(content_obj['headline'])
        summary = main_transulator[key].translate(content_obj['summary'])
        content = main_transulator[key].translate(content_obj['content'])
        output[key] = {
            "headline": headline,
            "summary": summary,
            "content": content
        }
    
    content_obj['languages'] = output

    return content_obj

uri = "mongodb+srv://newsappDBuser:W7itrf9uJqatKBjp@cluster0.2x3kk.mongodb.net/"

myclient = pymongo.MongoClient(uri)
mydb = myclient["news_db"]
mycol = mydb["news"]

tags = ["featurednews", "trendingnews", "breakingnews", "latestnews"]

class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://www.coindesk.com/tag/bitcoin/', 'https://www.coindesk.com/tag/ethereum/', 'https://www.coindesk.com/tag/binance-coin/']
    news_dict = {"https://www.coindesk.com/tag/bitcoin/": "Bitcoin News", "https://www.coindesk.com/tag/ethereum/": "Ethereum News", "https://www.coindesk.com/tag/binance-coin/": "Alt News"}
    news_dict_id = {"https://www.coindesk.com/tag/bitcoin/": "650d45276bb89616f4e084a0", "https://www.coindesk.com/tag/ethereum/": "6528eb0f97a0b6af8b874857", "https://www.coindesk.com/tag/binance-coin/": "650d45276bb89616f4e084a1"}
    data = {}

    def parse(self, response):
        news_list = response.xpath("/html/body/div[1]/div[2]/div/div/main/div/div/div[2]/div")

        for item in news_list:
           parse = item.get()
           soup = BeautifulSoup(parse, "html.parser")
           heading = soup.find('a', class_='card-title').text
           time = soup.find('div', class_='timing-data').find('span', class_='typography__StyledTypography-sc-owin6q-0').text
           author = soup.find('a', class_='ac-author').text
           summary = soup.find('span', class_='content-text').text
           href = soup.find('a', class_='card-title').get("href")
           redirected_url = "".join(["https://www.coindesk.com/", href])
           spiderURL = response.url
           img_srcset = soup.find('div', class_="img-block").find('a').find('picture').find('img').get('src')

           yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time, "author": author, "summary": summary, "spiderURL": spiderURL, "img_srcset": img_srcset})

    def parse_redirected(self, response):
        detail_data = response.css('div.composer-content').get()
        soup = BeautifulSoup(detail_data, "html.parser")
        content = soup.text

        n = random.random()
        spiderURL = response.meta['spiderURL']

        scrapted_content = {
            'imageUrls': response.meta['img_srcset'].split(","),
            'headline': response.meta['heading'],
            'category_id': self.news_dict_id[spiderURL], 
            'category': self.news_dict[spiderURL],
            'summary': response.meta['summary'],
            'content': content,
            'time': response.meta['time'],
            'author': response.meta['author'],
            'tags': random.sample(tags, 2),
            'views': 0
        }

        """ output = lang_trans(scrapted_content) """
        self.data[n] = scrapted_content
        """ mycol.insert_one(output) """


    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file)