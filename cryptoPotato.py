import json
import time
import scrapy
import random
from bs4 import BeautifulSoup
import pymongo

uri = "mongodb+srv://newsappDBuser:W7itrf9uJqatKBjp@cluster0.2x3kk.mongodb.net/"

myclient = pymongo.MongoClient(uri)
mydb = myclient["news_db"]
mycol = mydb["news"]

tags = ["featurednews", "trendingnews", "breakingnews", "latestnews"]


class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://cryptopotato.com/crypto-news/']
    data = {}

    def parse(self, response):
        news_list = response.css("ul.rpwe-ul > li").getall()

        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            heading = soup.find('h3', class_="rpwe-title").find('a').text           
            time = soup.find('time', class_="rpwe-time").text
            redirected_url = soup.find('h3', class_="rpwe-title").find('a').get('href')

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time})

    def parse_redirected(self, response):
        author = response.css('a.fn::text').get()
        imageUrls = response.css('figure > a::attr(href)').get()
        print(imageUrls)
        print("---------------------------------------------")

        """ n = random.random()
        content = ""
        for p in detail_data:
            soup = BeautifulSoup(p, "html.parser")
            content += soup.find('p').text

        scrapted_content = {
            'imageUrls': [response.meta['imageUrl']],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': content[:100],
            'content': content  ,
            'time': response.meta['time'],
            'author': author,
            'tags': random.sample(tags, 2),
            'views': 0
        }

        self.data[n] = scrapted_content
        mycol.insert_one(scrapted_content) """


    """ def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file) """         
