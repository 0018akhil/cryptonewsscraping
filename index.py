import random
from bson import ObjectId
import pymongo
import re

uri = "mongodb+srv://newsappDBuser:W7itrf9uJqatKBjp@cluster0.2x3kk.mongodb.net/"
myclient = pymongo.MongoClient(uri)
mydb = myclient["news_db"]
mycol = mydb["news"]

# news_list = list(mycol.find())

def create_unique_id_for_url(input_string):
    cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string).lower()
    url_friendly_string = re.sub(r'\s+', '-', cleaned_string)
    
    return url_friendly_string

# for news in news_list:
    # print(create_unique_id_for_url(news['headline']) + "-" + str(news['_id']))
    # mycol.update_one({"_id": news['_id']}, {"$set": {"url_id": "650d45276bb89616f4e084a0"}})

output = mycol.find()

"""
Add new field reading_time to all documents with randome time between 1 and 10 
 """
# for news in output:
#     mycol.update_one({"_id": news['_id']}, {"$set": {"reading_time": random.randint(1, 10)}})
# status: "published"

for news in output:
    mycol.update_one({"_id": news['_id']}, {"$set": {"status": "published"}})

newOutput = mycol.find()

for news in newOutput:
    print(news['status'])
