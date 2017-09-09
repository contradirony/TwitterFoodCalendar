import numpy as np
import pandas as pd
import recipe as rc
import re
from random import randint
import time 
import json
import requests
import os
import sys
#pip install --upgrade google-api-python-client
from googleapiclient.discovery import build

os.chdir(os.path.dirname(sys.argv[0]))

def google_url_shorten(url, api_key):
    # remember to enable https://console.developers.google.com/apis/api/urlshortener.googleapis.com/
   req_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + api_key
   payload = {'longUrl': url}
   headers = {'content-type': 'application/json'}
   r = requests.post(req_url, data=json.dumps(payload), headers=headers)
   resp = json.loads(r.text)
   return resp['id']


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']


def export_recipe_tweet(foodimage='', foodurl='', recipename='', recipeid='', googleAPIkey='', ingredient=''):
    ''' input image, url, recipename for text, id for reference and process image and append tweet to scheduler'''
    foodurlshort = google_url_shorten(foodurl, googleAPIkey)
    recipenamefix = recipename.lower().replace(" ", "").replace("'", "")
    foodtext = '''Today's recipe is {}: {} {}'''.format(recipename, foodurlshort, '#recipeoftheday')
    if foodimage != '':
        ingredientname=ingredient.lower().replace(" ", "").replace("'", "")
        imagename = '''images/{}_{}_{}.jpg'''.format(time.strftime('%Y-%m-%d'), ingredientname, recipeid)
        imagenamepath = '''{}/{}'''.format(os.getcwd(), imagename)
        os.system("wget -O {0} {1}".format(imagenamepath, foodimage))
    res = create_tweet(content=foodtext, image=imagenamepath, scheduledate=time.strftime('%Y-%m-%d'), 
                 scheduletime='{}:{}'.format(str(randint(14,16)).zfill(2), str(randint(0,59)).zfill(2)))
    return res


def create_tweet(savefile='/HOME_PATH/YOUR_FOLDER_NAME/TweetSchedule.txt', content='', 
                 image='', scheduledate='2017-05-06', scheduletime='07:00'):
    ''' format tweet as follows for scheduler and append:   
    a|Example tweet with attachment|image name.jpg|2017-03-26@00:00
    '''
    tweet_format='a'+'|'+content+'|'+image+'|'+scheduledate+'@'+scheduletime
    with open(savefile, 'a') as file:
        file.write('\n'+tweet_format)
    # TODO: should really be replaced with proper error handling...
    if len(content) > 140:
        return 'Tweet too long'
    else:
        return 'Tweet created'

def main():
    authdetailsdf=pd.read_csv("authdetails.csv", sep=';') 
    authdetails=dict(zip(list(authdetailsdf.key), list(authdetailsdf.value)))
    googleAPIkey = authdetails['googleAPIkey']
    csname = authdetails['googlecsname']
    spoon_api_key = authdetails['spoon_api_key']
    fooddata = pd.read_csv("fooddaysSimple.csv", sep='\t') 
    todayday = int(time.strftime('%d'))
    todaymonth = int(time.strftime('%m'))
    monthday = np.all([fooddata.Month==todaymonth, fooddata.Day==todayday], axis=0)
    datatoday = fooddata[monthday]
    # TODO: should write unit tests for three cases...
    if datatoday.shape[0]>0:
        ingredient = datatoday['Food'].values[0]
        # there is a national food day entry
        nationalday = 'National '+ingredient+' Day!'
        hashtag = '#'+'national'+ingredient.lower().replace(" ", "").replace("'", "")+'day'
        # get top google result for information about the day
        results = google_search(nationalday, googleAPIkey, csname, num=1)
        dayurlshort = google_url_shorten(results[0]['link'], googleAPIkey)
        # create one tweet for this
        nationaldaytweet = '''Happy {} Learn more about it at: {} {}'''.format(nationalday, dayurlshort, hashtag)
        create_tweet(content=nationaldaytweet, scheduledate=time.strftime('%Y-%m-%d'), 
        scheduletime='{}:{}'.format(str(randint(6,9)).zfill(2), str(randint(0,59)).zfill(2)))
        # get recipes that has the national food day in it as an ingredient
        # can be extended with starter, main, and dessert
        a=rc.RecipeClient(spoon_api_key)
        recipes=a.find_by_ingredients(ingredient)
        if len(recipes)>0:
            recipesdf = pd.DataFrame(recipes)
            recipesdf.sort_values(['likes', 'missedIngredientCount'], ascending=[False, False], inplace=True) #recipesdf.sort(['likes', 'missedIngredientCount'], ascending=[False, False], inplace=True)
            foodimageSpoon = recipesdf.iloc[0]['image']
            foodurlSpoon = re.sub('.png','', re.sub('.jpg', '', re.sub('recipeImages', 'recipe', foodimageSpoon)))
            recipenameSpoon = recipesdf.iloc[0]['title']
            recipeidSpoon = recipesdf.iloc[0]['id']
            res = export_recipe_tweet(foodimage=foodimageSpoon, foodurl=foodurlSpoon, recipename=recipenameSpoon,\
                                      recipeid=recipeidSpoon, googleAPIkey=googleAPIkey, ingredient=ingredient) 
            print(res)
        else:
            googlerecipe = google_search(ingredient+' recipe', googleAPIkey, csname, num=1)
            foodurlGoogle = googlerecipe[0]['link']
            foodimageGoogle = googlerecipe[0]['pagemap']['cse_image'][0]['src']
            recipenameGoogle = ingredient
            res = export_recipe_tweet(foodimage=foodimageGoogle, foodurl=foodurlGoogle, recipename=recipenameGoogle,\
                                      recipeid='google', googleAPIkey=googleAPIkey, ingredient=ingredient) 
            print(res)
    else:
        a=rc.RecipeClient(spoon_api_key)
        # get random joke   
        jokeattempt=0
        joke = a.random_joke()
        while jokeattempt <5:
            if len(joke['text']) < 141:
                create_tweet(content=joke['text'], scheduledate=time.strftime('%Y-%m-%d'), 
                             scheduletime='{}:{}'.format(str(randint(8,12)).zfill(2), str(randint(0,59)).zfill(2)))
                jokeattempt=100
                break
            else:
                joke = a.random_joke()
                jokeattempt+=1
        # ge random trivia
        triviaattempt=0
        trivia = a.random_trivia()
        while triviaattempt <5:
            if len(trivia['text']) < 141-len('Food fact: '):
                foodfact='Food fact: '+trivia['text']
                create_tweet(content=foodfact, scheduledate=time.strftime('%Y-%m-%d'), 
                             scheduletime='{}:{}'.format(str(randint(14,18)).zfill(2), str(randint(0,59)).zfill(2)))
                triviaattempt=100
                break
            else:
                trivia = a.random_trivia()
                triviaattempt+=1
        print('Joke and trivia for today')

 
if __name__ == '__main__':
    main()
