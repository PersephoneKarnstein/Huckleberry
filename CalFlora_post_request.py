import requests, urllib, ast, re #json
from bs4 import BeautifulSoup
from datetime import datetime as dt
import numpy as np

from model import *


HEADERS = {'Host': 'www.calflora.org',
 'Connection': 'keep-alive',
  'X-GWT-Module-Base': 'https',
   'X-GWT-Permutation': '796E3160B66F09A3EADB3F82FCFB6C20',
    'Origin': 'https',
     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
      'Content-Type': 'text/x-gwt-rpc; charset=UTF-8',
       'Accept': '*/*',
        'Referer': 'https',
         'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.9'}

payload = lambda scientific_name: f"7|0|25|https://www.calflora.org/entry/com.gmap3.DGrid2A/|835B15F29DDC753A8E097286A8997BBE|\
com.cfapp.client.wentry.WeedDataService|readPdas|java.util.HashMap/1797211028|I|[D/2047612875|java.lang.String/2004016611|taxon|\
{scientific_name}|georeferenced|t|addnloc|cch|wint|r|aor|DGR|hfil|R|griddiv|100|cell|xun|0|1|2|3|4|3|5|6|7|5|10|8|9|8|10|8|11|8|\
12|8|13|-5|8|14|-5|8|15|8|16|8|17|8|18|8|19|8|20|8|21|8|22|8|23|-5|8|24|8|25|2500|7|4|\
-125.000000000000|42.50000000000000|-114.000000000000|32.500000000000000|"

url = lambda key_number : f"https://www.calflora.org/cgi-bin/species_query.cgi?where-calrecnum={key_number}"


def compose_request(key_number):
    page = requests.get(url(key_number))
    soup = BeautifulSoup(page.content, features="lxml")
    scientific_name = (soup.select_one("#c-about > span").get_text()).strip()

    r = requests.post('https://www.calflora.org/app/weeddata', headers=HEADERS, data=payload(scientific_name))
    # data = r
    return ast.literal_eval(r.text[4:]) #weirdly calflora doesn't return things as json, so we need to convert the string into a list


def process_request_results(obs_list):
  extracted_data = np.asarray(["lon", "lat"])
  datetimes = ["obs_date"]

  for i, elem in enumerate(obs_list):
    if isinstance(obs_list[i], float) and isinstance(obs_list[i+1], float): #bc of how the response is structured, this will only grab the lat-lon pairs
      extracted_data = np.vstack(( extracted_data, np.asarray([float(obs_list[i]), float(obs_list[i+1])]) ))

    elif isinstance(elem, list): #finds the weird js list
    #Technically this should be in its own loop through the array, but because we know that the metadata list always comes after the list of coordinates, 
    #we can just have it in the same one
      plant_name = elem[4]
      pattern = re.compile("[0-9]{4}(\-[0-9]{2}){2}") #all the dates are stored as "YYYY-MM-DD"
      
      for j, metadatum in enumerate(elem):
        if pattern.match(metadatum): 
          obs_date = dt.strptime(metadatum, "%Y-%m-%d")
          datetimes.append(obs_date) 
  
  undated_obs = len(extracted_data)-len(datetimes)
  datetimes.extend([None]*undated_obs) #for unknown reasons, sometimes there are fewer metadata than there are observations.
  #a better implementation would attempt to associate the metadata with a specific lat/lon point based on the descriptive text;
  #however since the number of observations we will get from CalFlora is much smaller than the number from iNaturalist, and
  #since the date is arguably the least important of the data collected for each observation, especially as far back in history 
  #as many of these observations are, for the moment we will just assume that the listing was cut off and that the list of 
  #n metadata correspond to the *first* n observations.
  datetimes = np.asarray(datetimes).reshape((len(datetimes),1))
  
  # print(extracted_data,"\n=====================\n",datetimes,
  #   "\n=====================\n",np.shape(extracted_data), 
  #   np.shape(datetimes), 
  #   "\n\n\n\n\n\n")

  # print(f"{undated_obs} dates were unknown.")
  # extracted_data = extracted_data[:len(datetimes)]
  extracted_data = np.concatenate( (extracted_data, datetimes), axis=1)
  #so we end up with a np array of elements that look like [lon, lat, datetime]
  return plant_name, extracted_data

def to_dict(key_number):
  data = compose_request(key_number)
  plant_name, extracted = process_request_results(data)

  for obs in extracted[1:]:
    obs_dict = {"plant_id":key_number, "plant_name":plant_name, "lat":float(obs[1]), "lon":float(obs[0]), "elev":None, "obs_date":obs[2]}
      






