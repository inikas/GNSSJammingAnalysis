#Ioannis P. Nikas. January 2025. For the Aerospace Security Project at CSIS in Washington, D.C.
#Written with occasional help from Chat GPT from OpenAI
#This script helps download, clean, and save data form ADS_B exchange
import pandas as pd
import os

#for file handling
import json
import re #reject code
import pickle as pkl

#geo data and maps
import geopandas as gpd

#for online links
import requests
from bs4 import BeautifulSoup

#for dates
from dateutil import parser
from datetime import timedelta

#Change working directory to that of the script
script_dir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(script_dir) #doesn't get called unless you run this file as a stand alone file

#get the directory one above this one (the main folder)
parent_dir = os.path.dirname(script_dir)

#---------------START WORKER FUNCTIONS---------------
'''
#Function that takes a date in non dateutil and converts it and returns it as a dateutil object
#INPUT: Strings in any form, such as:
    "Feb 5, 2024",
    "2/4/2024",
    "2024-02-04",
    "5th February 2024",
    "04-02-2024",
    "February 5 2024"
#OUTPUT: dateime object: format: 2024-02-05 00:00:00 (all these will be GMT) in US format
'''
def convert_to_datetime(date):
    date_util = parser.parse(date) #use dateutil package and its parser to transform the date strings to date objects
    return date_util

'''
function to get the date as a string 
#INPUT: dateutil object 
#OUTPUT: date as a string in this format: '%Y-%m-%d', i.e. "2024-01-25"
'''
def get_date_util_string(date_util):
    return(date_util.strftime('%Y-%m-%d'))

'''
Given a start and end date, return a list of all dates between and including those dates
#INPUT: the start and end date as start_date and end_date, respectively, as dateutil objects
#OUTPUT: list of dateutil objects between the two dates, including the start and end dates
'''
def make_date_list(start_date, end_date):
    date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)] #add dates in range to list
    return date_list

'''
Get the day-specific url extension string for a date. This is concatanated with the general hist link. 
The directory online contains all the ADS-B json.gz files for that day 
#INPUT: a dateutil object 
#OUTPUT: extension as a string to add to the url. Example: "/2024/01/01/"
'''
def online_path_extension_for_historical_data(date):
    extension_string = "/" + str(date.year) + "/" + "{:02}".format(date.month) + "/" + "{:02}".format(date.day) + "/"
    return(extension_string)

'''
Get the directory extension for a date. This directory is located on the local device. 
It is added the main directory.
#INPUT: a dateutil object
#OUTPUT: directory extension. For example: "\\2024\\01\\01\\" - double slashes for WINDOWS directory link. 
#                                           Mac OS replaces these double slashes with "/"
'''
def local_directory_for_date(date):
    extension_string = os.path.join(str(date.year), "{:02}".format(date.month), "{:02}".format(date.day)) #will work for any system os
    return(extension_string)
#---------------END WORKER FUNCTIONS---------------


'''
Translate the ADS-B .json file to a GeoDataFrame and keep the parameters we want
#INPUTS: local_json_file_path - full file path to the .json file we want to convert on our system
#OUTPUTS: returns the GeoDataFrame. Columns are hardcoded within this function. Geometry is also added after convertin to GDF.
'''
def get_GeoDataFrame_from_json(local_json_file_path):
    time_df_rows = []   # Create an empty list to store the data from each flight in the time slice

    with open(local_json_file_path, "r", encoding="utf-8") as file: #open the .json file
        loaded_tracking_data = json.load(file) #returns a dictionary with the json objects within it
        for aircraft in loaded_tracking_data.get("aircraft", []): #for each flight - these are saved under an "aircraft" key
            #Sometimes the data is stored within a last position key. Try withouth, but if KeyError is thrown
            #that means it is stored within a subkey. Try that next. 
            try:
                information_to_add= [
                    aircraft["lat"], #lat
                    aircraft["lon"], #long
                    aircraft["nic"], # NIC
                    aircraft["rc"], #rc
                    aircraft["flight"] #get flight number
                ]
                time_df_rows.append(information_to_add) #add current data to saved rows
            except KeyError: #if exception is thrown
                try: #try last position key 
                    information_to_add= [
                        aircraft["lastPosition"]["lat"], #lat
                        aircraft["lastPosition"]["lon"], #long
                        aircraft["lastPosition"]["nic"], # NIC
                        aircraft["lastPosition"]["rc"], #rc
                        aircraft["lastPosition"]["flight"] #flight number
                    ]
                    time_df_rows.append(information_to_add)
                except KeyError: #if no last position info or missing flight number, just move on
                    continue   
    #create DataFrame from the list we've gathered with specified headers
    ADSB_data_headers= ["Latitude (deg)", "Longitude (deg)", "NIC", "R_C (m)", "Flight Number"] #in the order we added information above
    ADSB_data_df = pd.DataFrame(time_df_rows, columns = ADSB_data_headers)

    #create a geo data frame that adds a geometry column. Note that (x, y) are in the form of (long, lat)
    #note that this will add fifth column named 'geometry'. Also set the CRS
    ADSB_data_gdf = gpd.GeoDataFrame(ADSB_data_df, geometry=gpd.points_from_xy(ADSB_data_df[ADSB_data_headers[1]], ADSB_data_df[ADSB_data_headers[0]]), crs="EPSG:4326")

    #Now let's add a column of the country that the point is in
    country_map_directory = os.path.join(parent_dir, "maps", "ne_10m_admin_0_countries", "ne_10m_admin_0_countries.shp") #get country map directory 
    countries_land_borders_gdf = gpd.read_file(country_map_directory) # Load the shapefile - makes GeoDataFrame
    countries_land_borders_gdf = countries_land_borders_gdf[["ADMIN", "geometry"]]
    countries_land_borders_gdf = countries_land_borders_gdf.to_crs(ADSB_data_gdf.crs) #ensure the country gdf has the same CRS as our data

    #let's compare and add country ot the gdf in the pickle
    #Perform a spatial join to find which country each point falls into
    joined_gdf = gpd.sjoin(ADSB_data_gdf, countries_land_borders_gdf, how="left", predicate="within")
    #remove the index column that is added by only keeping original columns and the newly added ADMIN column with the names
    ADSB_data_gdf = joined_gdf[ADSB_data_gdf.columns.tolist() + ["ADMIN"]]  
    ADSB_data_gdf = ADSB_data_gdf.rename(columns={"ADMIN": "Country Name"}) #rename ADMIN column with country names

    #return the geo data frame 
    return ADSB_data_gdf

'''
Given a filepath to a .json ADSB file, convert to a geo data frame and save as a pkl
#INPUT: local_json_file_path, full filepath of the .json file we want to convert on the system
#OUTPUT: converst all json to pkl, also adds an extra folder to the directory for supp files
'''
def convert_ADSB_json_to_pkl(local_json_file_path):
    time_df = get_GeoDataFrame_from_json(local_json_file_path) #convert to dataframe and only keep relevant parameters for our analysis
    
    #save pkl in place of json
    pkl_file_path = os.path.splitext(local_json_file_path)[0] + ".pkl"  #get rid of the .json ending and replace with pkl
    time_df.to_pickle(pkl_file_path) #save data frame as pkl - I believe this overwrites if file exists
    os.remove(local_json_file_path) #delete .json file #note this command is taking longer than expected - slowing processes down

    #print out that we have downloaded the file
    #split and rejoin parts as they appear in directory with backslashes for just the directory that is deeper
    print(f"Downloaded: ", "\\".join(pkl_file_path.split("\\")[-5:])) 

'''
Download a file to a given directory. The function will first download the file as a .json.gz file, get rid of the .gz ending so
        so we can open the json file (it seems the ADS-B exchange files are not compressed into gz, anyways), keep the relevant data in a 
        GeoDataFrame, and lastly save that GeoDataFrame to a pkl file in the place of the original json file
#INPUTS: online_json_file_url, the url to the .json.gz file as a string. Example: "https://samples.adsbexchange.com/readsb-hist/2021/01/01/140000Z.json.gz"
        local_save_dir, the local directory to save the file at (this should correspond to a specifc day's folder)
#OUTPUTS: downloads pkl file of the file attached to the url with selected data
'''
def download_time_file(online_json_file_url, local_save_dir):
    #split the online url by the / marker and take the last index which is the name of the file, i.e "140000Z.json.gz"
    local_filepath_for_saving = os.path.join(local_save_dir, online_json_file_url.split("/")[-1]) 
    #print("enter")
    # If the .json.gz file already exists, overwrite it (delete it then write again)
    if os.path.exists(local_filepath_for_saving):
        os.remove(local_filepath_for_saving)
    #open the file and write it to the filepath we've created
    with requests.get(online_json_file_url, stream=True) as r: #get http request
        r.raise_for_status() # raise eorr 
        with open(local_filepath_for_saving, 'wb') as f: #open a new file at the filepath and prepare to write in binary
            for chunk in r.iter_content(chunk_size=8192): #read the file in small chunks (8192 KB at a time) - minimizes RAM usage
                f.write(chunk) #write to local file
    
    #get rid of the .gz ending
    new_file_path = os.path.splitext(local_filepath_for_saving)[0]
    os.rename(local_filepath_for_saving, new_file_path)
    #print("go convert to pkl")
    #open up and cleanup file to prepare for working with it and save as pkl
    convert_ADSB_json_to_pkl(new_file_path)

'''
Check if a particular file matches our sampling rate. If so return, True, otherwise False
#INPUTS: online_json_file_name, the name of the json file as it appears on the ADS-B website. Example: "013000Z.json.gz" 
        delta_t_min, (float or int) the sampling rate on which we should gather files for in minutes
#OUTPUTS: True if file is on sampling rate stored in delta_t_min, False otherwise
'''
def time_on_sampling_interval(online_json_file_name, delta_t_min):
    # Regex to match the format "HHMMSSZ.json.gz" Z for zulu time
    match = re.match(r"(\d{2})(\d{2})(\d{2})Z\.json\.gz", online_json_file_name)
    if match:
        hour, minute, second = map(int, match.groups())
        total_minutes_of_stamp = hour*60 + minute + second/60   #to check if multiple, find total minutes of this point 
        #check decimal and float case if sample is on sampling rate 
        if total_minutes_of_stamp % delta_t_min == 0.0 or total_minutes_of_stamp % delta_t_min == 0: 
            return True
    return False

'''
Download json files for a particular date
#INPUTS: online_date_page_url, url to the directory with the .json.gz files. such as: "https://samples.adsbexchange.com/readsb-hist/2021/01/01/"
        local_save_dir, String, the directory to which to save the .json.gz files
        delta_t_min, float or int, sampling rate in minutes
'''
def download_json_files_for_date(online_date_page_url, local_save_dir, delta_t_min):
    try:#ChatGPT helpful here, Get the HTML content of the page
        response = requests.get(online_date_page_url)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.content, 'html.parser') # Parse the HTML

        # Find all <a> tags and check for JSON file links
        for link in soup.find_all('a', href=True):
            online_json_file_url = link['href'] #get link name as a string of the json file online
            online_json_file_name = os.path.basename(online_json_file_url) # Extract the filename from the end (base) of the link
            if time_on_sampling_interval(online_json_file_name, delta_t_min): # Check if the file is on sampling rate
                #print("got file on time interval")
                if not online_json_file_url.startswith('http'): #If URL doesn't start with HTTP, make absolute
                    online_json_file_url = requests.compat.urljoin(online_date_page_url, online_json_file_url) #not sure what is going on here tbh
                download_time_file(online_json_file_url, local_save_dir)
    except requests.exceptions.HTTPError as error:   #if the link does not exist
        print(f"HTTP error occurred for {online_date_page_url}: {error}")


'''
Download ADS-B date given dates; either one start date, or start and end date to complete range
INPUTS: delta_t_min, sampling rate in minutes (float or int - but int makes more sense)
        dates_list, date util list of dates data is being downloaded for
OUTPUTS: downloads ADS-B json files into directories for dates
'''
def download_ADSB_data(delta_t_min, dates_list):
    #for each date, go through and scrape data from the proper link 
    for date in dates_list: 
        #Create the proper link for each date
        page_url = "https://samples.adsbexchange.com/readsb-hist" + online_path_extension_for_historical_data(date)  
        
        #use date info to save to proper directory - first make directory (this is the ADS-B folder, one directory above)
        local_saving_dir = os.path.join(parent_dir, "ADS_B_Data", local_directory_for_date(date)) #will work for any system os
        if not os.path.exists(local_saving_dir): #make directory if not created yet
            os.makedirs(local_saving_dir)
            print(f"Directory '{local_saving_dir}' created!")
        else:
            print(f"Directory '{local_saving_dir}' already exists. Overwriting.")

        #go online and get data using download function 
        download_json_files_for_date(page_url, local_saving_dir, delta_t_min)

'''
Main function to be called by other script with inputs to download data 
#INPUTS: start, date util start for data download or None
        end, date util start date for data download or None
        series, a list of dates in date util objects for download or None
        sampling_rate, dampling rate (int or float) in minutes 
#OUTPUT: downlaods data to directories as pkl files
'''
def main(start, end, series, sampling_rate):
    '''
    Run checks to ensure date inputs match format
    '''
    def run_checks():
        date_description = None #vars to display choices to user after
        dates_to_process = [] #dates to process will change based on user input 
        
        #check dates
        if series == None: #if no specified array 
            if (start == None) and (end == None): #no other dates
                raise ValueError("Need to enter valid date range.")
            elif (start == None) and (end != None): #if gave just an end date
                raise ValueError("Gave only end date. Need to give start date or specific dates in array form.")
            elif (start != None) and (end == None): #just gave start date
                dates_to_process = [start] #make sure is array, so need brackets
                date_description =get_date_util_string(start)
            elif (start != None) and (end != None): #gave start and end
                #make an array using our range fucntion, that covers all dates in between 
                if start < end: #only make range if start is before end
                    date_description = "range from " + get_date_util_string(start) + " to " + get_date_util_string(end)
                    dates_to_process = make_date_list(start, end)
                else: 
                    raise ValueError("For date range, start date must come before end date.")
        else: #gave array. use that
            if (start != None) or (end != None): #gave series and start or end date
                raise ValueError("If you select a series, you cannot select an additional start or end date. Select one of the other.")
            else:
                date_description = f"Dates: {', '.join(get_date_util_string(date) for date in series)}"
                dates_to_process = series
        
        #check sampling rate is given
        if sampling_rate ==None: #if no sampling rate
            raise ValueError("You need to input a sampling rate. None currently selected.")

        return True, date_description, dates_to_process,  #send back result of checks, date. we get here if no exceptions raised
    
    check_bool, date_desciprition, dates_to_process = run_checks() 
    if(check_bool):
        print("Downloading ADS-B data for " + date_desciprition, " at a sampling rate of ", sampling_rate, " minutes. \n")    
        download_ADSB_data(sampling_rate, dates_to_process)
        print("Download complete.")


#------------------------testing functions
'''
# Can run the function test_run(); within this file to test final output contents.
OUTPUT: downloads data for prescribed folder
'''
def test_download():
    delta_t_min = 30
    date_1_string = "June 1, 2018"
    date_1 = convert_to_datetime(date_1_string)
    date_2_string = "December 31, 2024"
    date_2 = convert_to_datetime(date_2_string)
    series = None
    main(date_1, date_2, series, delta_t_min)

'''
INPUTS: date_string, a string of a date to see contents for (make sure you have it downloaded - can use above function)
    this will check for 000000Z time on that day
OUTPUTS: shows sample pkl file contents for a day
'''
def test_show_downloaded(date_string):
    #test final result 
    date = convert_to_datetime(date_string)
    filepath = os.path.join(parent_dir, "ADS_B_Data", str(date.year), "{:02}".format(date.month), "{:02}".format(date.day), "000000Z.pkl")
    with open(filepath, 'rb') as file:
        data = pkl.load(file)
        print("Let's show the final data store din the pkl file: \n", filepath)
        print(data, "\n")
        print("The type of the file stored in the pkl file is: ", type(data))

test_show_downloaded("January 1, 2024")