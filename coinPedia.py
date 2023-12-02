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
    start_urls = ['https://coinpedia.org/bitcoin/']
    data = {}

    def parse(self, response):
        news_list = response.css('ul#posts-container > li').getall()

        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            author = soup.find('span', class_='meta-author').find('a').text
            time = soup.find('span', class_='date').text
            heading = soup.find('h2', class_='post-title').find('a').text
            redirected_url = soup.find('h2', class_='post-title').find('a').get('href')
            summary = soup.find('p', class_='post-excerpt').text

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, 'author': author, 'time': time, 'summary': summary})


    def parse_redirected(self, response):
        imageUrl = response.css('img.wp-post-image::attr(data-lazy-src)').get()
        detail_data = response.css('div.entry-content > p::text').getall()
        content = " ".join(detail_data)
        
        n = random.random()
        
        scrapted_content = {
            'imageUrls': [imageUrl],
            'headline': response.meta['heading'],
            'category_id': "6528eb0f97a0b6af8b874857", 
            'category': "Ethereum News",
            'summary': response.meta['summary'],
            'content': content,
            'time': response.meta['time'],
            'author': response.meta['author'],
            'tags': random.sample(tags, 2),
            'views': 0
        }

        """ output = lang_trans(scrapted_content)
        self.data[n] = output """
        mycol.insert_one(scrapted_content)

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file )