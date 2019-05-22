import requests, urllib, ast, re, warnings #json
import numpy as np

from bs4 import BeautifulSoup
from datetime import datetime as dt
from unicodedata import normalize as uni_normal


url = lambda key_number : f"https://www.calflora.org/cgi-bin/species_query.cgi?where-calrecnum={key_number}"


def test_taxon_page_goodness(soup_of_page):
  """Makes sure a page is a viable taxon report before scraping it"""
  try:
    no_record_text = soup_of_page.select("body > table:nth-child(4)")[0].b.get_text() #this will return "Sorry, no matching record found." when we have reached the last record
    
    if no_record_text == "Sorry, no matching record found.":
      page_good = False
      scientific_name_or_error_notes = "Reached last CalFlora record."
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
  #however, if the scientific name is no longer active, we would still get this far so we still need to check for that.

  try:
    name_inactive = soup_of_page.select_one("#c-name").i.get_text()
    scientific_name_or_error_notes = f'Name \x1b[1;30;47m{unicode_cleaner("#c-about > span", soup_of_page)}\x1b[0m is no longer in active use'
    page_good = False
  except AttributeError:
    pass

  calflora_about = soup_of_page.select_one("#c-about").get_text()
  #i'm pretty sure it shows this on every page.
  plant_nativity = (True if "is native to California" in calflora_about else False)
  if not plant_nativity:
    scientific_name_or_error_notes = f'\x1b[1;30;43m{unicode_cleaner("#c-about > span", soup_of_page)}\x1b[0m is not native to California'    
    page_good = False



  return page_good, scientific_name_or_error_notes



def unicode_cleaner(css_selector, soup):
  """A tiny function to remove non-breaking spaces and other annoying things found in web text"""
  gotten_text = soup.select_one(css_selector).get_text(strip=True)
  return uni_normal("NFKD", gotten_text)



def get_plant_taxon_report(key_number):
  """Pulls as much data as possible from the 'taxon report' page of a plant's CalFlora record"""
  page = requests.get(url(key_number))
  soup = BeautifulSoup(page.content, features="lxml")

  goodness = test_taxon_page_goodness(soup)

  if not goodness[0]:
    if goodness[1] == "Reached last CalFlora record.":
      raise Exception(goodness[1])

    else:
      warnings.warn(goodness[1]) #if test_taxon_page_goodness returns False, the second
    #part of the response will be an error message; if it returns True, the second part
    #of the response will be the scientific name. We still need to skip the page though:
      return None, None

  else: pass

  plant_data = {"plant_id":key_number,
    "sci_name":goodness[1],
    "plant_type":"",
    "min_height":None,
    "max_height":None,
    "plant_shape":[],
    "flower_color":[],
    "toxicity_bool": False,
    "toxicity_notes": "",   
    "native":False, #
    "rare":False,        
    "bloom_begin":None,     
    "bloom_end":None,
    "verbose_desc": "",      
    "technical_desc": "", #
    "calphotos_url":None, 
    "characteristics_url": f"https://www.calflora.org/entry/plantchar.html?crn={key_number}", 
    "jepson_url": None, 
    "calscape_url":None, 
    "usda_plants_url": None,
    "cnps_rare_url": None
    }


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
  # BLOOM PERIOD #
  ################
  if soup.select_one("#c-bloom").img:
    bloom_graph = soup.select_one("#c-bloom").img.attrs["src"]
    bloom_arg = re.search("(what=bloom&arg=\d{1,2}-\d{1,2}:1)", bloom_graph).group(1) 
    #slowly narrowing down the thing we grab because I'm not 100% sure they won't use it in weird ways
    bloom_begin, bloom_end = re.search("(\d{1,2}-\d{1,2})", bloom_arg).group(1).split("-")
    plant_data["bloom_begin"] = int(bloom_begin)
    plant_data["bloom_end"] = int(bloom_end)


  ################
  ### NATIVITY ###
  ################
  calflora_about = soup.select_one("#c-about").get_text()
  #i'm pretty sure it shows this on every page.
  plant_data["native"] = (True if "is native to California" in calflora_about else False)


  ################
  ### CALPHOTO ###
  ################
  try: #I think there should always be one, but just in case...
    calphotos_url = soup.select("#c-photosFrom")[0].find_all("a", string="CalPhotos")[0].attrs["href"]
    plant_data["calphotos_url"] = calphotos_url
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

  jepson_url = str(*[a for a in href_list if "ucjeps" in a])
  calscape_url = str(*[a for a in href_list if "calscape" in a])
  usda_plants_url = str(*[a for a in href_list if "usda" in a])

  for url_name in ["jepson_url", "calscape_url", "usda_plants_url"]:
    if url_name: plant_data[url_name] = locals()[url_name]

  ################
  #### RARITY ####
  ################
  try:
    rarity_tag = soup.select_one("#c-namestatus").select_one(".A10").find_all('a', string="CNPS")[0]
    plant_data["rare"] = True
    plant_data["cnps_rare_url"] = rarity_tag.attrs["href"]
  except IndexError:pass
  

  return plant_data, common_names



def get_plant_data_calscape(plant_data):
  """Pulls as much data as possible from the 'plant characteristics' page of a plant's CalFlora record

    plant_data should be inherited from get_plant_taxon_report() and look like this:
    plant_data = {'plant_id': 199,
      'sci_name': 'Allium howellii',
      'toxicity_bool': True,
      'toxicity_notes': 'MINOR',
      'native': False,
      "rare":False, 
      'bloom_period': None,
      'verbose_desc': '',
      'technical_desc': '',
      'calphotos_url': None,
      'characteristics_url': 'https://www.calflora.org/entry/plantchar.html?crn=199',
      'jepson_url': 'HTTP://ucjeps.berkeley.edu/eflora/eflora_display.php?tid=12587',
      'calscape_url': 'HTTP://calscape.org/Allium-howellii-()',
      'usda_plants_url': 'https://plants.usda.gov/java/nameSearch?mode=symbol&keywordquery=ALHO2',
      "cnps_rare_url": None}
  """
  if not plant_data["calscape_url"]:
    return plant_data
  else:
    try:
      page = requests.get(plant_data["calscape_url"])
      soup = BeautifulSoup(page.content, features="lxml")

      if soup.select_one(".about"):
        verbose_desc = soup.select_one(".about").get_text().split("\n")
        verbose_desc = " ".join([i.strip() for i in list(filter(None, verbose_desc))[1:]])
        plant_data['verbose_desc'] = (verbose_desc if len(verbose_desc)<995 else verbose_desc[:995]+"...")
      else: pass 

      if soup.find("legend", string="Plant Description"):
        plant_desc = soup.find("legend", string="Plant Description")
        for plant_attr in plant_desc.parent.find_all("div"):
          if "Plant Type" in plant_attr.get_text():
            plant_data["plant_type"] = list(filter(None, plant_attr.get_text().replace("\t", "").split('\n')))[-1]
            #see if it says if it's like a shrub or a tree or what
          elif "Form" in plant_attr.get_text():
            plant_data["plant_shape"] = list(filter(None, plant_attr.get_text().replace("\t", "").split('\n')))[-1].split(", ")
          
          elif "Flower Color" in plant_attr.get_text():
            plant_data["flower_color"] = list(filter(None, plant_attr.get_text().replace("\t", "").split('\n')))[-1].split(", ")
          
          else: pass

          if "Max. Height" in plant_attr.get_text():
            height_str = list(filter(None, plant_attr.get_text().replace("\t", "").split('\n')))[-1]
            if "ft" in height_str:
              meters = re.search("( ft \(\d{0,4}\.{0,1}\d{0,2}( -){0,1}( \d{0,4}\.{0,1}\d{0,2}){0,1} m\))", height_str)
              #look for the conversion to meters that Calscape does for each plant height and remove it. Because
              #feet are smaller (and listed first so presumably what was measured?) it should be a more accurate measure.

              possible_heights = [float(i) for i in height_str.replace(meters.group(1), "").split(" - ")]
            elif "in" in height_str:
              inches = re.search("( in \(\d{0,4}\.{0,1}\d{0,2}( -){0,1}( \d{0,4}\.{0,1}\d{0,2}){0,1} cm\))", height_str)
              possible_heights = [float(i)/12. for i in height_str.replace(inches.group(1), "").split(" - ")]

            else: raise Exception

            if len(possible_heights)==2:
              plant_data["min_height"], plant_data["max_height"] = possible_heights
            elif len(possible_heights) == 1:
              plant_data["max_height"] = possible_heights[0]
          else: pass
      else: pass
    except Exception:
      print(f"\x1b[1;37;45mAlert: {plant_data['sci_name']} is native, but Calscape has no page on it.\x1b[0m") #this is very sloppy but I don't want to handle the fact that calscape just sometimes doesn't have a page for that 
  return plant_data
