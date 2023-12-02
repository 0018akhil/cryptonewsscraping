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
    start_urls = ['https://blockworks.co/category/markets']
    data = {}

    def parse(self, response):
        news_list = response.xpath('/html/body/div[1]/div/main/section/div[1]/div[2]/div').getall()
        
        for news in news_list:            
            soup = BeautifulSoup(news, "html.parser")
            data = soup.find('a')
            if(data != None):
                siteUrl = "https://blockworks.co"
                redirectUrl = siteUrl + data.get('href')
                heading = soup.find_all('div')[2].find('a').get_text().strip()
                imageUrl = siteUrl + data.find('img').get('src')
                summary = soup.find_all('div')[3].find('p').get_text().strip()
                author = soup.find_all('div')[4].find('span').find('a').get_text().strip()
                time = soup.find_all('div')[4].find('time').get_text().strip()

                yield scrapy.Request(redirectUrl, callback=self.parse_redirected, meta={"heading": heading, "time": time, "author": author, "summary": summary, "imageUrl": imageUrl})

    def parse_redirected(self, response):
        div_data = response.css('div.prose').get()
        soup = BeautifulSoup(div_data, "html.parser")
        detailed_data = soup.get_text()

        n = random.random()
        
        scrapted_content = {
            'imageUrls': [response.meta['imageUrl']],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': response.meta['summary'],
            'content': detailed_data,
            'time': response.meta['time'],
            'author': response.meta['author'],
            'tags': random.sample(tags, 2),
            'views': 0
        }

        output = lang_trans(scrapted_content)
        self.data[n] = output
        mycol.insert_one(output)

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file )