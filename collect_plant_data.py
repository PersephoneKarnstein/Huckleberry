import requests, urllib, ast, re #json
import numpy as np

from bs4 import BeautifulSoup
from datetime import datetime as dt
from unicodedata import normalize as uni_normal


url = lambda key_number : f"https://www.calflora.org/cgi-bin/species_query.cgi?where-calrecnum={key_number}"


def test_taxon_page_goodness(soup_of_page):
  try:
    no_record_text = soup_of_page.select("body > table:nth-child(4)")[0].b.get_text() #this will return "Sorry, no matching record found." when we have reached the last record
    
    if no_record_text == "Sorry, no matching record found.":
      page_good = False
      scientific_name_or_error_notes = "\n\n\n\nReached last CalFlora record."
    else:
      page_good = False
      scientific_name_or_error_notes ="Unknown Error: page does not match known formats."
 
  except IndexError: #if it *doesn't* find that text in that position (i.e., if the record exists), it will raise an index error and come here.
    try:
      scientific_name_or_error_notes = unicode_cleaner("#c-about > span", soup_of_page)
      page_good = True

    except AttributeError:
      page_good = False
      scientific_name_or_error_notes = "Unknown Error: Scientific name not found."
      #I haven't actually seen it not be able to find a scientific name here, but it's possible.

  #ok so if we get to this point without raising an error, it means that you are on a page that (a) is a valid plant record and (b) has a species name.
  return page_good, scientific_name_or_error_notes

def unicode_cleaner(css_selector, soup):
  gotten_text = soup.select_one(css_selector).get_text(strip=True)
  return uni_normal("NFKD", gotten_text)

def get_plant_taxon_report(key_number):
  page = requests.get(url(key_number))
  soup = BeautifulSoup(page.content, features="lxml")

  goodness = test_taxon_page_goodness(soup)

  if not goodness[0]:
    raise Exception(goodness[1]) #if test_taxon_page_goodness returns False, the second
    #part of the response will be an error message; if it returns True, the second part
    #of the response will be the scientific name
  else: pass

  plant_data = {"plant_id":key_number,
    "sci_name":goodness[1],
    "toxicity_bool": False,
    "toxicity_notes": "",   
    "native":False,          #
    "bloom_period":None,     # 
    "verbose_desc": "",      #
    "technical_desc": "",    #
    "calphotos_url":None, 
    "characteristics_url": f"https://www.calflora.org/entry/plantchar.html?crn={key_number}", 
    "jepson_url": None, 
    "calscape_url":None, 
    "usda_plants_url": None,}


  ################
  ### TOXICITY ###
  ################

  #pull toxicity data first bc it weirdly only appears on this page
  community_notes = soup.select_one("#c-community").get_text().split()
  #the above works because if nothing else, the CalFlora taxon report page will
  #always 
  if 'Toxicity:' in community_notes:
    plant_data["toxicity_bool"] = True #the "Toxicity" field only appears on the page if the plant *is* toxic
    tox_notes = community_notes[community_notes.index('Toxicity:')+1]
    plant_data["toxicity_notes"] = tox_notes
  else: pass

  ################
  ### CALPHOTO ###
  ################
  try: #I think there should always be one, but just in case...
    calphotos_url = soup.select("#c-photosFrom")[0].find_all("a", string="CalPhotos")[0].attrs["href"]
  except IndexError:
    calphotos_url = None


  ################
  # COMMON NAMES #
  ################
  common_names = unicode_cleaner("#c-common", soup)
  common_names = [cn.strip() for cn in common_names.split(",")]


  ################
  ##### URLs #####
  ################
  href_list = [tag.attrs['href'] for i in [1,2,3] for tag in soup.select_one("#c-moreinfo"+str(i)).find_all("a")]

  jepson_url = [a for a in href_list if "ucjeps" in a][0]
  calscape_url = [a for a in href_list if "calscape" in a][0]
  usda_plants_url = [a for a in href_list if "usda" in a][0]

  for url_name in ["jepson_url", "calscape_url", "usda_plants_url"]:
    if url_name: plant_data[url_name] = locals()[url_name]



  return plant_data

def get_plant_data_characteristics(plant_data):
  # plant_data should be inherited from get_plant_taxon_report() and look like this:
  # 
  # plant_data = {'plant_id': 199,
  # 'sci_name': 'Allium howellii',
  # 'toxicity_bool': True,
  # 'toxicity_notes': 'MINOR',
  # 'native': False,
  # 'bloom_period': None,
  # 'verbose_desc': '',
  # 'technical_desc': '',
  # 'calphotos_url': None,
  # 'characteristics_url': 'https://www.calflora.org/entry/plantchar.html?crn=199',
  # 'jepson_url': 'HTTP://ucjeps.berkeley.edu/eflora/eflora_display.php?tid=12587',
  # 'calscape_url': 'HTTP://calscape.org/Allium-howellii-()',
  # 'usda_plants_url': 'https://plants.usda.gov/java/nameSearch?mode=symbol&keywordquery=ALHO2'}

  
