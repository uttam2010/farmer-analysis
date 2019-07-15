#import only as your need
import sys
import webbrowser, os
from twython import Twython  
import json
from string import punctuation
import re
import pandas as pd
from collections import Counter
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import gmplot
from datetime import timedelta as td, datetime
import numpy as np
import datetime
import unicodedata
import folium
import codecs
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


#filter special emogies
def BMP(s):
    #return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
    return "".join((i if ord(i) < 10000 else '\ufffd' for i in s))   

#return match our words in sentence
def check(sentence, words):
    for w in words:
       if w in sentence:
           return True
           break  

#load file for varify your twitter credentials
with open("twitter_credentials.json", "r") as file:  
    creds = json.load(file)

# set keywords to find more acurate tweets
with open("Key.txt", "r") as file1:  
    words= file1.read().split(',')
    

# Instantiate an object
python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

# Create our query--mixed,recent,popular -serching kewword 'farmers suicide'
query = {'q': 'farmers suicide',  
        'result_type': 'recent',
        'count': 1000,
        'lang': 'en',
        }

#You can data filter by following reasons
reasons=["crops","illness","debt", "borrow","daughter"]


#Search tweets from twitter API
print('.................farmer data storing.................')
headers=["user", "date", "text", "favorite_count", "location"]

#create dictionary  for store data a format
dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': [],'location': []}  

#fetch all tweets
for status in python_tweets.search(**query)['statuses']:    
    if (check(BMP(status['text']),words)) :
        dict_['text'].append(BMP(status['text']))
        dict_['user'].append(status['user']['screen_name'])
        dict_['date'].append(status['created_at'])    
        dict_['favorite_count'].append(status['favorite_count'])
        dict_['location'].append(status['user']['location'])


pd.set_option('display.max_columns', None)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)

#HTML TABLE print working-sorted by reasons
df = pd.DataFrame(dict_ )
df.sort_values(by=['user'], inplace=True)
#results are print on html
df.to_html('farmerstweet.html')

print('.................farmer data stored.')



#Download IP2LOCATION-LITE-DB9.CSV data from IP2Location ( https://lite.ip2location.com/database/ip-country-region-city-latitude-longitude-zipcode)

#Lets code for ***********generate MAP using IP2Location************************
print('.................Location Map writing.................')
location=dict_['location']

# getting county_code, place_name,latitude,longitude of India
dfnew = pd.read_csv("IP2LOCATION-LITE-DB9.CSV", header=None, usecols=[2,5,6,7])
#get only indian loactions
df=dfnew.loc[dfnew[2] == 'IN']

#Create location map acording tweet-data
folium_map = folium.Map(width = '100%',height=800,location=[20, 77], zoom_start=5, tiles="Stamen Terrain",min_lat=7, max_lat=35, min_lon=73, max_lon=90)

location = [el.replace(', India','') for el in location] #clear data 
location = list(filter(None, location)) # blank remove data


locationfreq={}
locationfreq=Counter(location) # create big cicle as frquency of location

for loc in locationfreq:
   for index, row in df.iterrows():
      if loc in row[5]:
         freq=locationfreq.get(loc,None)
	 
         lat, lon = row[6], row[7]
         folium.CircleMarker(location=(lat, lon),
                           radius = 6+ freq,
                           fill=True,
                           fill_color='#ff0000',
                           color = 'grey',
                           fill_opacity=0.7).add_to(folium_map)
         break
      


#Create map & print on html file
m = folium_map
html_string = m.get_root().render()
Html_file= open("farmermap.html","w")
Html_file.write(html_string)
m.save("farmermap.html")
Html_file.close()
print('.................Location Map Done.')



