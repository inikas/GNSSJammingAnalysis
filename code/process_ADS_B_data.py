#Ioannis P. Nikas. February 2025. For the Aerospace Security Project at CSIS in Washington, D.C.
#Written with occasional help from Chat GPT from OpenAI
#This script processess and plots the ADS_B_Data given user inputs 

import os
import pandas as pd
import numpy as np
import math
from collections import Counter #to count distinct number of objects

#for visualizations and maps
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import geopandas as gpd
import folium
from folium.plugins import TagFilterButton
import webbrowser #to open html map in browser
import mplcursors #cursor for plots

#for dates
from dateutil import parser
from datetime import timedelta


#Change working directory to that of the script
script_dir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(script_dir) #doesn't get called unless you run this file as a stand alone file

#parent directory (the main GNSS folder)
parent_dir = os.path.dirname(script_dir)

#--------------------------GLOBAL VARIABLES---------------------------------------
#NIC bins used for processing
NIC_bin_edges_to_process = None
NIC_colors = None
NIC_labels = None
#--------------------------END GLOBAL VARIABLES-----------------------------------


#--------------------------START Worker Functions---------------------------------
'''
#Check if a division operation is a whole number or not
#INPUT: degrees, the number of degrees we are dividing by binsize
#OUTPUT: exact_multiple_bool, boolean that tells us if dividend is a multiple of the divisor
        remainder, the reaminder of the division operation float or int depending on output
        A list of information in the following form [exact_multiple_bool, remainder]
'''
def division_information(degrees, bin_size):
    exact_multiple_bool = False #set as false, will be changed to true if condition met
    remainder = degrees % bin_size
    if bin_size == 0:
        return "Division by zero is not allowed."
    if degrees % bin_size == 0:
        exact_multiple_bool = True
    return [exact_multiple_bool, remainder]

'''
Round a number to the nearest integer, rounding 0.5 down
#INPUT: num, int of float to be rounded
#OUTPUT: rounded num, int
'''
def round_right_inclusive(num):
    #With chatGPT - Check if the number ends in .5
    if num - int(num) == 0.5: #int cuts the decimal component
        return int(num) #Round down
    else:
        return round(num) #Use normal rounding for other cases

'''
#Function to take a date range and return dates we want to pull data from 
#INPUT: Strings in any form, such as:
    "Feb 5, 2024",
    "2/4/2024",
    "2024-02-04",
    "5th February 2024",
    "04-02-2024",
    "February 5 2024"
OUTPUT: dateime object: format: 2024-02-05 00:00:00 (all these will be GMT) in US format
'''
def convert_to_datetime(date):
    #use dateutil package and its parser to transform the date strings to date objects
    date_util = parser.parse(date)
    return date_util
'''
Given a start and end date, make an array of dates with every consecutive date between and including those dates
#INPUT: date_1, date_util object. The start date
        date_2, date_util_object. The end date
#OUTPUT: list of dateutil objects between the two dates, inclusive of bounds
'''
def make_date_list(date_1, date_2):
    date_list = [date_1 + timedelta(days=x) for x in range((date_2 - date_1).days + 1)]
    return date_list

'''
Get a date_util object in the form of a string
#INPUT: date_util, a date_util object 
#OUTPUT: date in string form: "%Y-%m-%d", i.e. "2024-01-25"
'''
def get_date_util_string(date_util):
    return(date_util.strftime('%Y-%m-%d'))
#-----------------------------END Worker Functions---------------------


#----------------START PLOT FUNCTIONS--------------------   
'''
This plots on a map created with the natural world maps.
Plot the NIC data from a gdf by plotting all counts and coloring based on bins
#INPUT: gdf,  gdf to plot - !! make sure you are calling a copy of the gdf so we don't change the original when computing the levels !!
        date_util (optional) - dateutil object- pass if plotting full day's data.
#OUTPUT: plot of of data, NIC points colored based on bin
'''
def plot_gdf_naturalworld_maps(gdf, date_util = None):
    #cut data to bins and add a column that tells us
    gdf['Level of Jamming'] = pd.cut(gdf['NIC'], bins=NIC_bin_edges_to_process, labels=NIC_labels)
    gdf = gdf.dropna(subset=['Level of Jamming']) #drop values that are not in our bins

    #let's get the map
    land_file_directory = os.path.join(parent_dir, "maps", "ne_10m_land.shp")
    ocean_file_directory = os.path.join(parent_dir, "maps", "ne_10m_ocean.shp")
    world_land = gpd.read_file(land_file_directory)
    world_ocean =gpd.read_file(ocean_file_directory)
    
    # We can now plot GeoDataFrame and NIC values on the world
    ax = world_land.plot(color='lightgrey', edgecolor='darkgrey', figsize=(16, 9))  # Base world map
    world_ocean.plot(ax = ax, color='lightblue', edgecolor='darkgrey')  # Base ocean map
    
    gdf.plot(ax=ax, column= gdf['Level of Jamming'], cmap=ListedColormap(NIC_colors), markersize=2, legend=True)

    #add formatting to plot
    ax.set_title("Jamming on " + get_date_util_string(date_util))
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title("Level of Jamming: ", fontsize=16)
    plt.show()

'''
This plots on a folium map. Tutorial: https://geopandas.org/en/stable/gallery/plotting_with_folium.html
Plot the NIC data from a gdf by plotting all counts and coloring based on bins
#INPUT: gdf,  gdf to plot - !! make sure you are calling a copy of the gdf so we don't change the original when computing the levels !!
        needs to have a NIC column
        key, a string indicating if the map is of averaged values or of the raw. Two option: "raw" or "averaged." If something else, just
            saves with that custom string
#OUTPUT: folium map with NIC points colored based on bins, html format
'''
def plot_gdf_folium_map(gdf, key):
    #cut data to bins and add a column that tells us the level of jamming
    gdf['Level of Jamming'] = pd.cut(gdf['NIC'], bins=NIC_bin_edges_to_process, labels=NIC_labels)
    gdf = gdf.dropna(subset=['Level of Jamming']) #drop values that are not in our bins, i.e. that return na when binned
    headers = gdf.columns 

    #initialize a folium map
    folium_map = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=5)
    
    # Add points with colors based on jamming level to the folium map
    for _, row in gdf.iterrows():
        colors_mapping = dict(zip(NIC_labels, NIC_colors))
        color = colors_mapping[row['Level of Jamming']]  # Get color for the jamming level
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1,
            tags = [row['Level of Jamming'], row[headers[2]]], #add tags that we can use to filer (level, NIC, and flight number)
            popup=f"Level of Jamming: {row['Level of Jamming']}, NIC: {row[headers[2]]} " #What will pop up whnen you hover over the point
        ).add_to(folium_map)

    #let's add a filter so you can pick what points to show
    TagFilterButton(NIC_labels).add_to(folium_map)

    #save and display the map in browser based on the key
    if key == "raw":
        folium_map.save(os.path.join(parent_dir, "outputs", "map_raw.html")) #save to output file
        # webbrowser.open(os.path.join(parent_dir, "outputs", "map_raw.html")) #un-comment to open automatically in browser
    elif key == "averaged":
        folium_map.save(os.path.join(parent_dir, "outputs", "map_averaged.html")) #un-comment to open automatically in browser
        # webbrowser.open(os.path.join(parent_dir, "outputs", "map_averaged.html")) #un-comment to open automatically in browser
    else: #neither of the valid options was given, so just add key and save
        folium_map.save(os.path.join(parent_dir, "outputs", "map_averaged.html", "map", key, ".html"))
        # webbrowser.open(os.path.join(parent_dir, "outputs", "map_averaged.html", "map", key, ".html")) #un-comment to open automatically in browser
    
'''
Take gdf with NIC values. Box them into cells of given lat and long dimensions and keep the average NIC value
#INPUT: NIC_data_frame, a dataframe, or a gdf (gdf inherits from data frame)
#OUTPUT: a Geo Data Frame of average NIC at center of boxes that were determined given the cell dimensions
'''
def get_NIC_data_boxed_averages(NIC_data_frame):
    #get headers
    headers = NIC_data_frame.columns
   
    # Define bin sizes for latitude and longitude
    #Effectively what we are doing is first deciding how big we want the bins to be
    #Note that with small decimal degrees (less than 0.25) this breaks -- something with the rounding/floats
    lat_bin_size = 0.25
    long_bin_size = 0.25

    # Calculate the number of bins needed for resolution. remember rows are first in index, then column
    #this means that: [row, column] = [lat, long]
    #initialize two properties to hold the number of bins. We will need these values are also the Number of indeces we will need in our grid
    lat_grid_num_bins = None
    long_grid_num_bins = None

    #to catch the extra interval if the latt/long value does not divide perfectly into the degrees
    #use round function to go to closest integer. this means everything centers at the closest integer of bin
    #at end we plot in the middle of the bin

    #looking to make intervals INCLUSIVE ON THE RIGHT, ESCLUSIVE ON THE LEFT
    lat_division = division_information(180, lat_bin_size)
    #first check if the number of degrees is a multiple of the bin size
    if lat_division[0]: #0 index is boolean
        lat_grid_num_bins = int(180 / lat_bin_size) + 1
    elif lat_division[1] <= (lat_bin_size/2): #if remaining space is less than half of our bin
        lat_grid_num_bins =  math.floor(180/lat_bin_size) + 1 #a bin centered at every multiple, and one extra at zero will suffice 
    else: #this means we have remaining space and we will need an extra bin centered at 180
        lat_grid_num_bins =  math.floor(180/lat_bin_size) + 2

    long_division = division_information(360, long_bin_size)
    #first check if the number of degrees is a multiple of the bin size
    if long_division[0]: #0 index is boolean
        long_grid_num_bins = int(360 / long_bin_size) + 1 #want bin centered at each multiple and zero
    elif long_division[1] <= (long_bin_size/2): #if remaining space is less than half of our bin
        long_grid_num_bins =  math.floor(360/long_bin_size) + 1 #a bin centered at every multiple, and one extra at zero will suffice 
    else: #this means we have remaining space and we will need an extra bin centered at 180
        long_grid_num_bins =  math.floor(180/long_bin_size) + 2

    # Create a 2D array to represent the grid
    lat_long_NIC_as_grid = np.full((lat_grid_num_bins, long_grid_num_bins), None)

    #Go through each row in the NIC data and assign to at point in the discrete grid
    for index, row in NIC_data_frame.iterrows():
        #round means point is rounded down to the nearest integer,
        #This means for the midpoint that it belongs to in the bin is half step higher 
         #if bin lies at the every end of the range, i don't want to make another bin that exceeds 
        #Since a bin is centered at every multiple of the bin size and zero, dividing and rounding the 
        #degrees results in the INDEX of the associated bin
        row_index_on_grid = round_right_inclusive((row[headers[0]] + 90) / lat_bin_size)
        col_index_on_grid = round_right_inclusive((row[headers[1]] + 180) / long_bin_size)

        #NOTICE - we throw out values that are 0, since those are unreliable points
        #only add to be processed if the value is not equal to zero
        if row[headers[2]] != 0:
            if lat_long_NIC_as_grid[row_index_on_grid][col_index_on_grid] is None:  #If the cell is empty
                lat_long_NIC_as_grid[row_index_on_grid][col_index_on_grid] = [row[headers[2]]]  #Initialize it with a new array containing the value
            else:
                lat_long_NIC_as_grid[row_index_on_grid][col_index_on_grid].append(row[headers[2]])  #Append the value to the existing array
    
    #now we need to go through and AVERAGE the points within the grid
    #Loop through each row and column
    for i in range(len(lat_long_NIC_as_grid)): #len() returns number of rows
        for j in range(len(lat_long_NIC_as_grid[i])): #len(index) returns number of columns in row i
            # Check if the cell contains a list (or array)
            if isinstance(lat_long_NIC_as_grid[i][j], list):
                # Calculate the average and replace the cell's value
                #using custom rounding fucntion that rounds to nearest int, with 0.5 rounding down
                lat_long_NIC_as_grid[i][j] = round_right_inclusive(np.mean(lat_long_NIC_as_grid[i][j]))

    #now convert the grid into a data frame using the index of each position
    #first just make a new array that we can convert to a dataframe as lat and long
    holding_for_new_data_frame = []

    #Loop through the 2D array and create (lat, long - IN NEW FRAME, value) tuples
    #Again, the row index represents which multiple of the bin size a point corresponds to
    for i in range(len(lat_long_NIC_as_grid)):  # oop through rows (latitude)
        for j in range(len(lat_long_NIC_as_grid[i])):  #Loop through columns (longitude)
            row_index = i  #Row index is latitude
            column_index = j  #Column index is longitude
            value = lat_long_NIC_as_grid[i][j]  #The value in the cell
            transform_back_lat = None #empty values to hold transformed lat and long
            transform_back_long = None
            if value != None: #only procede if there is a value present 
                transform_back_lat = row_index*lat_bin_size - 90
                transform_back_long = column_index*long_bin_size - 180
            holding_for_new_data_frame.append([transform_back_lat, transform_back_long, value]) #convert back to real frame
    # Create a DataFrame from the data
    final_NIC_boxed_data_frame = pd.DataFrame(holding_for_new_data_frame, columns=[headers[0], headers[1], headers[2]])

    final_NIC_boxed_gdf = final_NIC_boxed_data_frame = gpd.GeoDataFrame(final_NIC_boxed_data_frame, geometry=gpd.points_from_xy(final_NIC_boxed_data_frame[headers[1]], final_NIC_boxed_data_frame[headers[0]]), crs="EPSG:4326")

    return final_NIC_boxed_gdf

'''
Return a GeoDataFrame that has points only within the specifeid custom polygon region 
#INPUTS: time_slice_gdf, the time slice GeoDataFrame
        custom_polygon, a string of a custom region to be looked at
#OUTPUT: within_polygon_gdf, a GeoDataFrame with points within the custom polygon region
'''
def get_gdf_in_custom_polygon(custom_polygon_gdf, custom_polygon):
    #get the shape file gdf
    polygon_directory = os.path.join(os.getcwd(), "maps","custom_polygons", custom_polygon +".shp")
    polygon_gdf = gpd.read_file(polygon_directory) # Load the shapefile - makes Geo Data Frame
    polygon_gdf = polygon_gdf.to_crs(custom_polygon_gdf.crs)
    polygon_gdf = polygon_gdf[["geometry"]] #just keep geometry - all we need to compare to

    #now let"s join the time slice gdf with the region
    gdf_in_polygon = gpd.sjoin(custom_polygon_gdf, polygon_gdf, how="left", predicate="within")
    gdf_in_polygon["is_within_polygon"] = gdf_in_polygon["index_right"].notna() #only keep the the rows that are not na, i.e. in the polygon
    #only keep rows that are in polygon, i.e. the ones that have true in the is_wihin_polygon column
    time_slice_in_polygon_gdf = gdf_in_polygon[gdf_in_polygon["is_within_polygon"] == True] 
    time_slice_in_polygon_gdf = time_slice_in_polygon_gdf.drop(["index_right", "is_within_polygon"], axis=1)

    #return the geo data frame 
    return time_slice_in_polygon_gdf

'''
Put together a full day's worth of data into one big gdf. Filter out for chosen regions if necessary
#INPUTS: date_util, date_util object for the date we want to get data for 
        specified_country, string of a country that is pre-saved in our files
       custom polygon is a polygon defined by user if they want data over a custom polygon
#OUTPUTS: all the days data in one GeoDataFrame
'''
def get_full_day_gdf(date_util, specified_country = None, custom_polygon = None):
    #get teh directory path for the day's data. use the date information to get the folder path (year/month/day)
    date_directory = os.path.join(parent_dir, "ADS_B_Data", str(date_util.year), "{:02}".format(date_util.month), "{:02}".format(date_util.day)) #will work for any system os
    #get the file names within the day's folder. only keep files ending in .pkl - these are the times slice gdfs
    date_pkl_file_names = [f for f in os.listdir(date_directory) if f.endswith('.pkl')]    
    
    #create emtpy data to fill with day's data
    full_date_gdf = gpd.GeoDataFrame()

    #loop through every time slice file for the date and add to the full day gdf
    for time_slice_pkl_file_name in date_pkl_file_names:
        time_slice_pkl_file_path = os.path.join(date_directory, time_slice_pkl_file_name) #will work for any system os
        time_slice_gdf = pd.read_pickle(time_slice_pkl_file_path) #get's a copy of the gdf we have saved in the pkl file
        if specified_country != None: #check if known region given
            time_slice_gdf = time_slice_gdf[time_slice_gdf["Country Name"] == specified_country] #only keep rows that fall in country
        elif custom_polygon != None: 
            #filter out parameters only inside polygon - call a copy of the time slice to avoid any unwanted memory saving
            time_slice_gdf = get_gdf_in_custom_polygon(time_slice_gdf.copy(), custom_polygon) #get gdf in custom pplygon 
        #at end add time slice to the full date gdf
        full_date_gdf = pd.concat([full_date_gdf, time_slice_gdf], ignore_index=True)

    return full_date_gdf

#----------------------------Flight number Stats------------------------------------
'''
Count the number of UNIQUE flights and the percentage that are within the selected jamming ranges for ONE DATE
#INPUTS: full_day_gdf, the gdf of the day to process
        date_util, the date in question as a date util object
#OUTPUTS: a one-row data frame with the number of flights in each NIC bin and the percentage of each type, index is the date in date_util form
'''
def get_flight_counts_and_percents_day(full_day_gdf, date_util):
    data_headers = full_day_gdf.columns #this also has the geometry from the gdf

    #lets count how many instances of each bin of Nic we have
    #create an array to hold the corresponding counts for each bin 
    #the 0th index corresponds to the 1st bin, 1st index to the 2nd, etc.
    num_bins = len(NIC_bin_edges_to_process) - 1 
    #lets add new columns to hold the percentages
    flight_counts_and_percents_headers_list = NIC_labels.copy() #we'll add on to the original ones
    for i in range(num_bins): #make a new bin holder for each bin in num bins
        flight_counts_and_percents_headers_list.append("flights % Jam: " + NIC_labels[i])    
    #print("Headers: ", counts_and_percents_headers_list, ". Type: ", type(counts_and_percents_headers_list), ". Shape: ", np.shape(counts_and_percents_headers_list))

    #now let's calculate the actual number of unique flights in each bin
    flight_counts_and_percents_array = np.zeros( (1, num_bins*2) ) #1 x 2*numbins array to hold - i.e a 1-dimensional array
    for i in range(num_bins): #for each bin - index 0 refers to the first bin 
        #use logic to get either false (0) or true (1) on wheter value in data frame falls in the bin for each bin
        #then only take the rows of the full_day_gdf that have true in the inside of the next line
        gdf_in_bin = full_day_gdf[ (full_day_gdf[data_headers[2]] > NIC_bin_edges_to_process[i]) & (full_day_gdf[data_headers[2]] <= NIC_bin_edges_to_process[i + 1]) ]
        flight_num_list = gdf_in_bin[data_headers[4]]#get list of the flight numbers
        num_unique_flights = len(Counter(flight_num_list)) #get the number of unique flight numbers
        flight_counts_and_percents_array[0, i]= num_unique_flights #append the number of flights to the storage array
    #now lets do the percentages for the flights
    total_num_flights = flight_counts_and_percents_array.sum()#first get total number of flights in observation period
    #print("The array is ", np.round(flight_counts_and_percents_array, 2), " ---- Total flights: ", total_num_flights, "for", date_util)
    for i in range(num_bins): #for each index in our counting array, starting at 0
        percent_flights_jam = ( flight_counts_and_percents_array[0, i]/total_num_flights )*100 #calc percent
        flight_counts_and_percents_array[0, i+num_bins] = percent_flights_jam #add percent to spot in storage array

    #convert date into a data frame
    flight_counts_and_percents_df = pd.DataFrame(flight_counts_and_percents_array, columns = flight_counts_and_percents_headers_list)
    flight_counts_and_percents_df.index = [date_util.strftime('%Y-%m-%d')]
    
    return(flight_counts_and_percents_df)


'''
Returns a one-row data frame that stores the counts and percentages of each jamming type specified for ONE DATE
#INPUT: full_day_gdf, the gdf of the day to process
        date_util, date util object for the day being processed
#OUTPUT: A 1-d data frame that stores the number of ADS-B counts in the first n/2 columns (n = number of bins) in each bin,
        and stores the percentage of each of those instances with respect to the total sum in the second set of n/2 columns
'''
def get_jamming_counts_and_percents_day(full_day_gdf, date_util):
    data_headers = full_day_gdf.columns #this also has the geometry from the gdf

    #lets count how many instances of each bin of Nic we have
    #create an array to hold the corresponding counts for each bin 
    #the 0th index corresponds to the 1st bin, 1st index to the 2nd, etc.
    num_bins = len(NIC_bin_edges_to_process) - 1 
    #lets add new columns to hold the percentages
    counts_and_percents_headers_list = NIC_labels.copy() 
    for i in range(num_bins): #make a new bin holder for each bin in num bins
         counts_and_percents_headers_list.append("counts % Jam: " + NIC_labels[i])    
    #print("Headers: ", counts_and_percents_headers_list, ". Type: ", type(counts_and_percents_headers_list), ". Shape: ", np.shape(counts_and_percents_headers_list))
    
    #calculate counts and add to a storage list
    counts_and_percents_array = np.empty( (1, num_bins*2) ) #1 x 2*numbins array to hold 
    for i in range(num_bins): #for each index in our counting array, starting at 0
        #use logic to get either false (0) or true (1) on whether value in data frame falls in the bin for each bin
        bin_count = ( (full_day_gdf[data_headers[2]] > NIC_bin_edges_to_process[i]) & (full_day_gdf[data_headers[2]] <= NIC_bin_edges_to_process[i + 1]) ).sum()
        counts_and_percents_array[0, i]= bin_count
    total_counts = counts_and_percents_array.sum() #only counts in so far, total counts is just sum of array
    #calculate percentage for each count and add to storage list
    for i in range(num_bins): #for each index in our counting array, starting at 0
        percent_jam = ( counts_and_percents_array[0, i]/total_counts )*100
        counts_and_percents_array[0, i+num_bins] = percent_jam #percents are next set so add numbins to index
    print("Array: ", counts_and_percents_array, ". Array shape: ", counts_and_percents_array.shape)
    
    #convert date into a data frame
    counts_and_percents_df = pd.DataFrame(counts_and_percents_array, columns = counts_and_percents_headers_list)
    counts_and_percents_df.index = [date_util.strftime('%Y-%m-%d')]
    
    return(counts_and_percents_df)

'''
Returns a data frame of the statistics foe either instances of jamming or flight number counts over a DATE RANGE (at least one date)
The first n_bins/2 columns represent the instances of the metric, and the second set of n_bins/2 columns represent the perecntages of each 
bin with respect to the total observed - the total is only that of all the bins entered, not the original sample of ADS-B data
#INPUT: key, a string of either "flights" or "counts" to specify which stats to gather
        dates, a list of dates to process
        specified_country, either None or a string of the specified country from the pre-made list
        custom_polygon, either None or a string of the custom polygon from the saved shp files
#OUTPUT: Data frame with dates as the indeces, and stats in the columns. first n_bins/2 columns are instances, next set are percentages
'''
def get_stats_date_range(key, dates, specified_country=None, custom_polygon = None):
    #make headers. for both counts and percents
    #lets count how many instances of each bin of Nic we have
    #create an array to hold the corresponding counts for each bin 
    #the 0th index corresponds to the 1st bin, 1st index to the 2nd, etc.
    num_bins = len(NIC_bin_edges_to_process) - 1 
    #lets add new columns to hold the percentages
    stats_headers_list = NIC_labels.copy() 
    for i in range(num_bins): #make a new bin holder for each bin in num bins
         stats_headers_list.append(key + " % Jam: " + NIC_labels[i])
    stats_range_df = pd.DataFrame(columns=stats_headers_list) #data frame to hold the counts

   
    #go through dates and get statistic depending on entry, append to the range count df
    if key == "flights":
        for date_util in dates:
            #get the full gdf for the date - pass parameters and gdf will take care of regions if selected
            full_day_gdf = get_full_day_gdf(date_util, specified_country = specified_country, custom_polygon = custom_polygon) 
            #print("Got full day gdf for ", get_date_util_string(date_util))
            flight_counts_and_percents_date_df = get_flight_counts_and_percents_day(full_day_gdf, date_util)
            if stats_range_df.empty: #if the stats are empty, i.e. this is the first frame to add
                flight_counts_and_percents_date_df.columns = stats_headers_list #set column names to match our stats and set stats equal to it
                stats_range_df = flight_counts_and_percents_date_df
            else:
                stats_range_df = pd.concat([stats_range_df, flight_counts_and_percents_date_df])     
    elif key == "counts":
        for date_util in dates:
            #get the full gdf for the date - pass parameters and gdf will take care of regions if selected
            full_day_gdf = get_full_day_gdf(date_util, specified_country = specified_country, custom_polygon = custom_polygon) 
            #print("Got full day gdf for ", get_date_util_string(date_util))
            jamming_counts_and_percents_date_df = get_jamming_counts_and_percents_day(full_day_gdf, date_util)
            if stats_range_df.empty: #if the stats are empty, i.e. this is the first frame to add
                jamming_counts_and_percents_date_df.columns = stats_headers_list #set column names to match our stats and set stats equal to it
                stats_range_df = jamming_counts_and_percents_date_df
            else:
                stats_range_df = pd.concat([stats_range_df, jamming_counts_and_percents_date_df])        
    else:
        print("INVALID KEY")#if key not either of preset options, alert user and stop
        return
    return stats_range_df


#-----------------------------------------Plot Statistics------------------------------
'''
Plot counts (number) of each type of jamming level in a bar graph 
#INPUT: jamming_counts_range_df,  which can have >= 1 row of a day's data. Index should be the date of the row. 
        flight_stats_date_range, same format as jamming_counts_range-df but with number of flights and percentages
        The first n/2 columns are the counts themselves, and the next n/2
        region_description, string of the region we are working. Is none if not passed, which corresponds to full world
#OUTPUT: plot of the counts, stacked bar charts. 
'''
def bar_plot_stats(jamming_counts_range_df, flight_stats_date_range, region_description):
    #plot bar graph of counts 
    num_bins = len(NIC_bin_edges_to_process) - 1  
    
    #make plots
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True)
    
    #do counts first
    counts_df = jamming_counts_range_df.iloc[:, 0:num_bins]
    counts_df.plot(kind = "bar", stacked = True, colormap = ListedColormap(NIC_colors), ax = axes[0, 0])
    #format top plot
    axes[0, 0].set_title("Jamming Counts over " + str(region_description if region_description is not None else "the Whole World"))
    axes[0, 0].set_ylabel("Jamming Counts") 
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.6)  # Horizontal gridlines with dashed lines
    # Add interactive tooltips - from GPT
    cursor1 = mplcursors.cursor(axes[0, 0].containers, hover=True)
    @cursor1.connect("add")
    def on_hover(sel):
        sel.annotation.set_text(f"{int(sel.artist.datavalues[sel.index])}")  # Show bar value which is counts, an integer (whole number)
        sel.annotation.get_bbox_patch().set(fc="lightgray", alpha=0.85)  # Background color
        sel.annotation.get_bbox_patch().set_edgecolor("black")  # Border color
        sel.annotation.set_fontsize(10)  # Increase font size
        sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.3")  # Rounded edges
        sel.annotation.set_visible(True)  # Ensure it's visible

    #now let's add percents on the bottom of the counts
    counts_percents_df = jamming_counts_range_df.iloc[:, num_bins:num_bins*2]
    counts_percents_df.plot(kind = "bar", stacked = True, colormap = ListedColormap(NIC_colors), ax = axes[1, 0])
    #formatting
    axes[1, 0].legend_.remove()
    axes[1, 0].set_title("Percentage at Each Jamming Level Over " +str(region_description if region_description is not None else "the Whole World")) #add region name otherwise is full world)
    axes[1, 0].set_ylabel("Percentage of Counts at Each Level")
    axes[1, 0].set_xlabel("Date")
    axes[1, 0].grid(axis='y', linestyle='--', alpha=0.6)  # Horizontal gridlines with dashed lines
    axes[1, 0].set_xticklabels(jamming_counts_range_df.index, rotation=55)  # Rotate the x-axis labels to horizontal (0 degrees)
    # Add interactive tooltips - from GPT
    cursor2 = mplcursors.cursor(axes[1, 0].containers, hover=True)
    @cursor2.connect("add")
    def on_hover(sel):
        sel.annotation.set_text(f"{round(sel.artist.datavalues[sel.index], 2)}")  # Show bar value which is counts, an integer (whole number)
        sel.annotation.get_bbox_patch().set(fc="lightgray", alpha=0.85)  # Background color
        sel.annotation.get_bbox_patch().set_edgecolor("black")  # Border color
        sel.annotation.set_fontsize(10)  # Increase font size
        sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.3")  # Rounded edges
        sel.annotation.set_visible(True)  # Ensure it's visible
    
    #now for flight stats 
    flights_df = flight_stats_date_range.iloc[:, 0:num_bins]
    flights_df.plot(kind = "bar", stacked = True, colormap = ListedColormap(NIC_colors), ax = axes[0, 1])
    #format top plot
    axes[0, 1].set_title("Number of Flights Jammed over " + str(region_description if region_description is not None else "the Whole World"))
    axes[0, 1].set_ylabel("Number of Flights Jammed") 
    axes[0, 1].grid(axis='y', linestyle='--', alpha=0.6)  # Horizontal gridlines with dashed lines
    # Add interactive tooltips - from GPT
    cursor3 = mplcursors.cursor(axes[0, 1].containers, hover=True)
    @cursor3.connect("add")
    def on_hover(sel):
        sel.annotation.set_text(f"{int(sel.artist.datavalues[sel.index])}")  # Show bar value which is counts, an integer (whole number)
        sel.annotation.get_bbox_patch().set(fc="lightgray", alpha=0.85)  # Background color
        sel.annotation.get_bbox_patch().set_edgecolor("black")  # Border color
        sel.annotation.set_fontsize(10)  # Increase font size
        sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.3")  # Rounded edges
        sel.annotation.set_visible(True)  # Ensure it's visible

    #now let's add flight stats percents on the bottom
    flights_percents_df = flight_stats_date_range.iloc[:, num_bins:num_bins*2]
    flights_percents_df.plot(kind = "bar", stacked = True, colormap = ListedColormap(NIC_colors), ax = axes[1, 1])
    #formatting
    axes[1, 1].legend_.remove()
    axes[1, 1].set_title("Percentage for Each Jamming Level Over " +str(region_description if region_description is not None else "the Whole World")) #add region name otherwise is full world)
    axes[1, 1].set_ylabel("Percentage of Flights at Each Level")
    axes[1, 1].set_xlabel("Date")
    axes[1, 1].grid(axis='y', linestyle='--', alpha=0.6)  # Horizontal gridlines with dashed lines
    axes[1, 1].set_xticklabels(flight_stats_date_range.index, rotation=55)  # Rotate the x-axis labels to horizontal (0 degrees)
    # Add interactive tooltips - from GPT
    cursor4 = mplcursors.cursor(axes[1, 1].containers, hover=True)
    @cursor4.connect("add")
    def on_hover(sel):
        sel.annotation.set_text(f"{round(sel.artist.datavalues[sel.index], 2)}")  # Show bar value which is counts, an integer (whole number)
        sel.annotation.get_bbox_patch().set(fc="lightgray", alpha=0.85)  # Background color
        sel.annotation.get_bbox_patch().set_edgecolor("black")  # Border color
        sel.annotation.set_fontsize(10)  # Increase font size
        sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.3")  # Rounded edges
        sel.annotation.set_visible(True)  # Ensure it's visible

    plt.tight_layout() # Adjust layout to ensure everything fits
    plt.show()


#-------------------------------------------MAIN FUNCTION CALL-----------------------------
'''
Main function to run script based on inputs given from the GUI
#INPUTS:start, dateutil  object of start date or None
        end, dateutil  object of end date or None
        series, list of dates series, in date util objets or None
        world, boolean if world or not is selected, 
        region, string, name of the country from the pre-made list or None
        custom, string, name of shp file from custom polygons or None
        NIC_bin_edges, edges of the bins in a list
        NIC_colors_hex_list, list of hex code for each bin
#OUTPUT: Display statistics graphs - also makes map of the first date that is inputted
'''
def main(start, end, series, world, region, custom, NIC_bin_edges, NIC_colors_hex_list):
    
    '''
    Runs checks to ensure data has not been entered in an over or underconstrained fashion
    '''
    def run_checks():
        date_description = None #vars to display choices to user after
        region_description = None 
        dates_to_process = [] #dates to process will change based on user input 
        
        #check dates
        if series == None: #if no specified array 
            if (start == None) and (end == None): #no other dates
                raise ValueError("Need to enter valid date range.")
            elif (start == None) and (end != None): #if gave just an end date
                raise ValueError("Gave only end date. Need to give start date or specific dates in array form.")
            elif (start != None) and (end == None): #just gave start date
                dates_to_process = [start] #make sure is array, so need brackets
                date_description = get_date_util_string(start)
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
    
        #check regions
        if world == True:  
            if region !=None or custom != None:
                raise ValueError("You cannot select the whole world and another region. Pick only one.")
            region_description = "the whole world"
        else: 
            if region == None and custom == None: #no locatio was given 
                raise ValueError("Select a region to process data over")
            elif region != None and custom != None: #gave both preset and custom 
                raise ValueError("You cannot select both a preset and custom region. Select one.")
            elif region != None:
                region_description = region
            elif custom != None: 
                region_description = custom
    
        #check NIC bin edges and colors 
        num_bins = len(NIC_bin_edges) - 1
        num_colors = len(NIC_colors_hex_list)
        if num_bins != num_colors:
            raise ValueError("Inputted a different number of colors than NIC bins. Make sure they are the same.")
        if NIC_bin_edges == None or []: #if empty or none
            raise ValueError("No NIC bin edges. Add NIC bin edges.")
        elif num_bins > 10:
            raise ValueError("You enetered more than 10 bins. Only 10 allowed (limited by hardcodedc colors). Sorry and Thanks.")
        #check that NIC bins are with range (nothing less than zero, all less than their right neighbor)
        for i in range(len(NIC_bin_edges) - 1): #will hit every index until the second to last one value in NIC_bin_edges
            if NIC_bin_edges[i] >= NIC_bin_edges[i+1]:
                raise ValueError ("Error. You have inputted a lower bound in the NIC bins that is greater than or equal to the upper bound of the bin. \n")
        
        #if got here, NIC is good, update edges in script along with colors and labesl
        global NIC_bin_edges_to_process
        global NIC_colors
        global NIC_labels 

        #update bin edges and color hex list to stored vars 
        NIC_bin_edges_to_process = NIC_bin_edges
        NIC_colors = NIC_colors_hex_list

        #create labels for bins
        labels_temp = [] #array to hold the acutal bins to display to the user
        for i in range(0, num_bins): #this will go to one less than the num_bins startint with 1
            labels_temp.append("NIC = (" + str(NIC_bin_edges[i])  + ", " + str(NIC_bin_edges[i+1]) + "]")
        NIC_labels = labels_temp

        return True, date_description, region_description, dates_to_process #we get here if no exceptions raised

    check_bool, date_description, region_description, dates_to_process = run_checks()   #call the run checks function 
    if(check_bool): #if checks successful
        print("Processing data for " + date_description + " over ", region_description, " with the following bins ", NIC_labels)

        #get first date, and its gdf and averaged gdf over the grid
        first_date = dates_to_process[0]
        gdf = get_full_day_gdf(first_date, specified_country = region, custom_polygon = custom)
        averaged_gdf = get_NIC_data_boxed_averages(gdf.copy())
        #show maps
        plot_gdf_folium_map(gdf, key = "raw") #can change these keys to what you would like
        plot_gdf_folium_map(averaged_gdf, key = "averaged")
        
        #CALL PROCESSING FUNCTIONS AND DISPLAY RESULTS
        flight_stats = get_stats_date_range("flights", dates_to_process, specified_country=region, custom_polygon = custom)
        counts_stats = get_stats_date_range("counts", dates_to_process, specified_country=region, custom_polygon = custom)
        bar_plot_stats(counts_stats, flight_stats, region_description)

