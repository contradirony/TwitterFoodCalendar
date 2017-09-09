# code from https://raw.githubusercontent.com/boxcarton/watson-recipe-bot/master/souschef/recipe.py
# instructions adapted from https://medium.com/ibm-watson-developer-cloud/how-to-build-a-recipe-slack-bot-using-watson-conversation-and-spoonacular-api-487eacaf01d4

''' FYI
pip uninstall dotenv
pip install python-dotenv'''


import requests
import json, os
from dotenv import load_dotenv

class RecipeClient:
  def __init__(self, api_key):
    self. endpoint = \
      'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/'
    self.api_key = api_key


  def find_by_ingredients(self, ingredients, nres=5):
    url = self.endpoint + 'recipes/findByIngredients'

    params = {
      'fillIngredients': False,
      'ingredients': ingredients, #string
      'limitLicense': False,
      'number': nres,
      'ranking': 1
    }

    headers={
      "X-Mashape-Key": self.api_key,
      "Accept": "application/json"
    }

    return requests.get(url, params=params, headers=headers).json()

  def find_by_cuisine(self, cuisine):
    url = self.endpoint + "recipes/search"

    payload = {
      'number': 5,
      'query': ' ',
      'cuisine': cuisine
    }
    headers={ 'X-Mashape-Key': self.api_key }

    return requests.get(url, 
                        params=payload, 
                        headers=headers).json()['results']

  def get_info_by_id(self, id):
    url = self.endpoint + "recipes/" + str(id) + "/information"
    params = {'includeNutrition': False }
    headers = {'X-Mashape-Key': self.api_key}

    return requests.get(url, params=params, headers=headers).json()

  def get_steps_by_id(self, id):
    url = self.endpoint + "recipes/" + str(id) + "/analyzedInstructions"
    params = {'stepBreakdown': True}
    headers={'X-Mashape-Key': self.api_key}

    return requests.get(url, params=params, headers=headers).json()


  # added summarize_recipe to original class
  def summarize_recipe(self, recipe_id):
    url = self.endpoint + 'recipes/' + recipe_id + '/summary'
    headers={
      "X-Mashape-Key": self.api_key,
      "Accept": "application/json"
    }
    return requests.get(url, headers=headers).json()

  # added get random_joke to original class
  def random_joke(self):
    url = self.endpoint + 'food/jokes/random'
    headers={
      "X-Mashape-Key": self.api_key,
      "Accept": "application/json"
    }
    return requests.get(url, headers=headers).json()

  # added get random_trivia to original class
  def random_trivia(self):
    url = self.endpoint + 'food/trivia/random'
    headers={
      "X-Mashape-Key": self.api_key,
      "Accept": "application/json"
    }
    return requests.get(url, headers=headers).json()

 # add search recipes complex
  def find_complex(self, ingredients, nres=5, coursetype='main course'):
    url = self.endpoint + 'recipes/searchComplex'

    params = {
      'query': ingredients,
      'fillIngredients': False,
      'ingredients': ingredients, #string
      'limitLicense': False,
      'offset': nres,
      'ranking': 1,
      'type': coursetype
    }

    headers={
      "X-Mashape-Key": self.api_key,
      "Accept": "application/json"
    }

    return requests.get(url, params=params, headers=headers).json()
