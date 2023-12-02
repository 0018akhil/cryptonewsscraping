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

    main_transulator = [{'DE':translator_german}, {'JP':translator_japanese}, {'IT':translator_italian}, {'PT':translator_portuguese}, {'FR':translator_french}, {'ES':translator_spanish}]

    for key, val in main_transulator:
        headline = val.translate(text=content_obj['headline'])
        summary = val.translate(text=content_obj['summary'])
        content = val.translate(text=content_obj['content'])
        output[key] = {
            "headline": headline,
            "summary": summary,
            "content": content
        }
    
    content_obj['language'] = output

    return content_obj

uri = "mongodb+srv://newsappDBuser:W7itrf9uJqatKBjp@cluster0.2x3kk.mongodb.net/"

myclient = pymongo.MongoClient(uri)
mydb = myclient["news_db"]
mycol = mydb["news"]

tags = ["featurednews", "trendingnews", "breakingnews", "latestnews"]


class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://beincrypto.com/bitcoin-news/']
    news_dict = {"https://beincrypto.com/bitcoin-news/": "Bitcoin News",
                 "https://www.coindesk.com/tag/ethereum/": "Ethereum News", "https://www.coindesk.com/tag/binance-coin/": "BinanceCoin News"}
    data = {}

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        news_list = response.css("main.main > div:nth-of-type(2) > div").getall()

        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            imageUrl = soup.find('img', class_="object-cover").get("data-srcset")
            redirected_url = soup.find('a').get("href")
            heading = soup.find('a', class_="hover:no-underline").text
            time = soup.find('time', class_="ago").text
            
            yield scrapy.Request(redirected_url, headers=headers, callback=self.parse_redirected, meta={"heading": heading, "time": time, "imageUrl": imageUrl})

    def parse_redirected(self, response):
        detail_data = response.css('div.entry-content-inner').get()
        summary = response.css('div.entry-content-inner > p > strong::text').get()        
        
        scrapted_content = {
            'imageUrls': response.meta['imageUrl'],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': summary,
            'content': detail_data,
            'time': response.meta['time'],
            'author': None,
            'tags': random.sample(tags, 2),
            'views': 0
        }

        n = random.random()
        output = lang_trans(scrapted_content)
        self.data[n] = output
    
        """ mycol.insert_one(scrapted_content) """
  

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file)  