import requests, urllib, ast, re #json
from bs4 import BeautifulSoup
from datetime import datetime as dt
import numpy as np

def get_plant_data(key_number)
  page = requests.get(url(key_number))
  soup = BeautifulSoup(page.content, features="lxml")

  try:
    no_record_text = soup.select("body > table:nth-child(4)")[0].b.get_text() #this will return "Sorry, no matching record found." when we have reached the last record
    if no_record_text == "Sorry, no matching record found.":
      raise Exception("\n\n\n\nReached last CalFlora record.")
    else: raise Exception("Unknown Error: page does not match known formats.")
  except IndexError: #if it *doesn't* find that text in that position (i.e., if the record exists), it will raise an index error and come here.
    try:
      scientific_name = (soup.select_one("#c-about > span").get_text()).strip()
    except AttributeError:
      raise Exception("Unknown Error: Scientific name not found.")
      #I haven't actually seen it not be able to find a scientific name here, but it's possible.

  #ok so if we get to this point without raising an error, it means that you are on a page that (a) is a valid plant record and (b) has a species name.

  # return scientific_name
    
