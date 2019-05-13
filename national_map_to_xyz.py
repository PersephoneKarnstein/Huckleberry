import zipfile, subprocess, urllib.request, shutil, os

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

total_downloads = file_len("/Users/persephonek/Desktop/Programs/plant_project/ned111_20190426_152612.txt")

i = 1
for line in open("/Users/persephonek/Desktop/Programs/plant_project/ned111_20190426_152612.txt"):
    url = line.strip()
    #'url' looks like either
    #https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/ArcGrid/USGS_NED_1_n37w120_ArcGrid.zip
    #or
    #https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/ArcGrid/n36w118.zip

    filename = url.split("/")[-1]
    #now 'filename' looks like either n42w118.zip
    #or USGS_NED_1_n38w121_ArcGrid.zip

    filepath = '/Users/persephonek/Desktop/Programs/plant_project/'+filename
    unzipped_path = filepath[:-4]

    try:
        corner_id = filename.split('_')[3]
        #if it looks like USGS_NED_1_n38w121_ArcGrid.zip, the
        #corner_id will look like n38w121
    except IndexError:
        corner_id = filename[:-4]
        #if it looks like n42w118.zip, the corner_id will look like n42w118

    print(f'Download {i} of {total_downloads}:\nBeginning file download {filename}')

    urllib.request.urlretrieve(url, filepath) #save the data from the url to plant_project/blah

    print(f"Unarchiving {filename}...")
    zip_ref = zipfile.ZipFile(filepath, 'r')
    zip_ref.extractall(unzipped_path) #extract the zip archive to a folder with the same name but no .zip
    zip_ref.close()

    print(f"Converting {filename} to XYZ...")
    arcgrid_file = unzipped_path+'/grd'+corner_id+"_1" #the file within the folder that gdal can translate
    gdal_command = f"gdal_translate -of XYZ {arcgrid_file} /Users/persephonek/Desktop/Programs/plant_project/elevation/{corner_id}.txt"
    #translate to xyz coords
    subprocess.run(gdal_command, shell=True)


    os.remove(filepath) #remove the zip archive

    shutil.rmtree(unzipped_path) #we're done with the downloaded files now that they've been translated, so delete that directory tree

    print(f"Coordinate conversion complete for {filename}.\n\n")
    i+=1
