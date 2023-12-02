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
    start_urls = ['https://insidebitcoins.com/news']
    data = {}

    def parse(self, response):
        articles = response.css('main#main > article').getall()

        for aricle in articles:
            soup = BeautifulSoup(aricle, "html.parser")
            heading = soup.find('a', class_="article-header-title").text
            author = soup.find('div', class_="inline-author-meta").find('a').find('span').text
            time = soup.find('span', class_="ptime").find('time').text
            redirected_url = soup.find('a', class_="article-header-title").get('href')

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time, "author": author})


    def parse_redirected(self, response):
        img_srcset = response.css('div.ib-post-thumbnail-desktop > img::attr(src)').get()
        detailed_data = response.css('div.entry-content > p').getall()
        content = ""
        for data in detailed_data:
            soup = BeautifulSoup(data, "html.parser")
            content += soup.text

        n = random.random()
        
        scrapted_content = {
            'imageUrls': [img_srcset],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': content[:100],
            'content': content,
            'time': response.meta['time'],
            'author': response.meta['author'],
            'tags': random.sample(tags, 2),
            'views': 0
        }

        output = lang_trans(scrapted_content)
        mycol.insert_one(output)
        self.data[n] = scrapted_content

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file)