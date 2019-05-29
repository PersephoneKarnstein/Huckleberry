from urllib import parse
import requests



def get_inat_obs(sci_name):
    name_str = parse.quote(sci_name)
    pagenum = 1

    url = lambda name_str, pagenum : f"https://api.inaturalist.org/v1/observations?place_id=14&taxon_name=\
        {name_str}&quality_grade=needs_id&page={pagenum}&per_page=200&order=desc&order_by=created_at"

    r = requests.get(url(name_str, pagenum))

    resultpage = r.json()

    added_obs = []

    if resultpage["total_results"] == 0: return None

    else:
        total_pages = int(resultpage["total_results"]/200) + (0 if resultpage["total_results"]%200==0 else 1)
        while pagenum <= total_pages:
            for obs in r.json()["results"]:
                lat, lon = [float(a) for a in obs["location"].split(",")]
                added_obs.append([lon, lat])


            pagenum+=1

        return added_obs

