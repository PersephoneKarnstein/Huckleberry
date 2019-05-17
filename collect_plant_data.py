import requests, urllib, ast, re #json
from bs4 import BeautifulSoup
from datetime import datetime as dt
import numpy as np

url = lambda key_number : f"https://www.calflora.org/cgi-bin/species_query.cgi?where-calrecnum={key_number}"


def test_taxon_page_goodness(soup_of_page):
  try:
    no_record_text = soup.select("body > table:nth-child(4)")[0].b.get_text() #this will return "Sorry, no matching record found." when we have reached the last record
    
    if no_record_text == "Sorry, no matching record found.":
      page_good = False
      scientific_name_or_error_notes = "\n\n\n\nReached last CalFlora record."
    else:
      page_good = False
      scientific_name_or_error_notes ="Unknown Error: page does not match known formats."
 
  except IndexError: #if it *doesn't* find that text in that position (i.e., if the record exists), it will raise an index error and come here.
    try:
      scientific_name_or_error_notes = (soup.select_one("#c-about > span").get_text()).strip()
      page_good = True

    except AttributeError:
      page_good = False
      scientific_name_or_error_notes = "Unknown Error: Scientific name not found."
      #I haven't actually seen it not be able to find a scientific name here, but it's possible.

  #ok so if we get to this point without raising an error, it means that you are on a page that (a) is a valid plant record and (b) has a species name.
  return page_good, scientific_name_or_error_notes


def get_plant_data(key_number):
  page = requests.get(url(key_number))
  soup = BeautifulSoup(page.content, features="lxml")

  goodness = test_taxon_page_goodness(soup)

  if not goodness[0]:
    raise Exception(goodness[1]) #if test_taxon_page_goodness returns False, the second
    #part of the response will be an error message; if it returns True, the second part
    #of the response will be the scientific name
  else: pass

  plant_data = {"plant_id":key_number, "sci_name":goodness[1], "toxicity_bool"=False,\
  "toxicity_notes"="", "calphotos_url"="", "native"=False, "bloom_period"=None,\
   "verbose_desc"=""}

  #pull toxicity data first bc it weirdly only appears on this page
  community_notes = soup.select("#c-community")[0].get_text().split()
  #the above works because if nothing else, the CalFlora taxon report page will
  #always 
  if 'Toxicity:' in community_notes:
    plant_data["toxicity_bool"] = True #the "Toxicity" field only appears on the page if the plant *is* toxic
    tox_notes = plant_data[community_notes.index('Toxicity:')+1]
    plant_data["toxicity_notes"] = tox_notes
  else: pass

  try: #I think there should always be one, but just in case...
    calphotos_url = soup.select("#c-photosFrom")[0].find_all("a", string="CalPhotos")[0].attrs["href"]
  except IndexError:
    calphotos_url = None