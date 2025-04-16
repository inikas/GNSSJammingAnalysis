#Ioannis P. Nikas. January 2025. For the Aerospace Security Project at CSIS in Washington, D.C.
#Written with occasional help from Chat GPT from OpenAI
#Script to create a simple GUI for the user to interact with the GPS Jamming tool

import os 
import pickle 

import tkinter
from tkinter import colorchooser #for color list
from tkinter import ttk #ttk is a widget module
#if you include the * you can cause several tkinter.ttk widgets (Button, Checkbutton, Entry, Frame, Label, LabelFrame, Menubutton, PanedWindow, Radiobutton, Scale and Scrollbar) 
# to automatically replace the Tk widgets. I have opted out of this
from tkcalendar import Calendar
#for dates
from dateutil import parser

#Change working directory to that of the script
script_dir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(script_dir) 

#get the directory one above this one (the main folder)
parent_dir = os.path.dirname(script_dir)

#import the other scripts for processing and downloading. These are in the same directory as this script 
import process_ADS_B_data
import get_ADS_B_data


#----------------------WORKER FUNCTIONS----------------
'''
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
Get a date_util object in the form of a string
#INPUT: date_util, a date_util object 
#OUTPUT: date in string form: "%Y-%m-%d", i.e. "2024-01-25"
'''
def get_date_util_string(date_util):
    return(date_util.strftime('%Y-%m-%d'))
#------------------------END WORKER FUNCTIONS---------------


#-----------------START GLOBAL SETUP----------------------------
#list of admin countries are saved in a pkl file. open and load in as a list of the 258 names
countries_file_name = "countries_list.pkl"
countires_pkl_file = open(countries_file_name, 'rb') #load the file
admin_list = pickle.load(countires_pkl_file) #get the list (the data within)
admin_list.sort() #sort alphabetically
#print("List", admin_list, "Length ", len(admin_list), " of type ", type(admin_list))

#global variables to keep track of selections. These will change
NIC_bin_edges = None
NIC_colors_hex_list = None #list of hex colors as strings
#first for the get data 
download_start_date_util = None 
download_start_date_string = None
download_end_date_string = None
download_end_date_util  = None
download_date_list_util = [] #list to hold list of dates for series of dateutil objects
#now for the processing dates
start_date_string = None
start_date_util = None
end_date_string = None
end_date_util  = None
date_list_util = [] #list to hold list of dates for series of dateutil objects

#-------------------------------MAIN AND SUB FRAMES------------
#create the processing widget frame within the root
root_window = tkinter.Tk(className = " GNSS Jamming Quantifying") #constuct a toplevel Tk widget, ususally the main window of an app

#subframes
credit_frame = tkinter.Frame(root_window, borderwidth=3) #to show credits for the tool
credit_frame.grid(column = 0, row = 1, sticky = 'nw')
credit_label = ttk.Label(credit_frame, wraplength=450, justify='left', 
                        text= "Ioannis Nikas. March 2025. Center for Strategic and International Studies - Aerospace Security Project.").grid(column = 0, row = 0)
get_data_frame = tkinter.Frame(root_window, relief="groove", borderwidth=3) #frame for downloading data
get_data_frame.grid(column = 0, row = 0, sticky = 'nwe')  #create frame for the get data frame
process_data_frame = tkinter.Frame(root_window, relief="groove", borderwidth=3) #NOTE: I'll be making tkinger Frames but hte rest are ttk widgets
process_data_frame.grid(column = 1, row = 0, sticky = 'nwe') #make a sub frame in the root for user entries

#on first run, make none labels for date selection fields
#for data download
download_start_date_label = ttk.Label(get_data_frame, text= "None")
download_start_date_label.grid(column=1, row=1, sticky='w')
download_end_date_label = ttk.Label(get_data_frame, text= "None")
download_end_date_label.grid(column=1, row=2, sticky='w')
#for data processing
start_date_label = ttk.Label(process_data_frame, text= "None")
start_date_label.grid(column=1, row=1, sticky='w')
end_date_label = ttk.Label(process_data_frame, text= "None")
end_date_label.grid(column=1, row=2, sticky='w')

'''
Function to make a calendar popup for entering dates of interest
#INPUT: type, a number corresponding to either start date or end date
        "start" corresponsd to start, "end" corresponds to end date
#OUTPUT: calendar popup that changes the start date Var, as well
'''
def open_calendar_popup(type):
    toplevel = tkinter.Toplevel(root_window)  # Create a new popup window
    toplevel.title("Select a " + type +" date")

    # Create a Calendar widget
    cal = Calendar(toplevel, selectmode="day", year=2024, month=1, day=1)
    cal.pack(pady=10)
    current_selected_date = get_date_util_string(cal.selection_get())#gets date on open 
    
    #gets the selected date in the calendar popup
    def add_selected_date():
        #make clear global variables will change 
        global download_start_date_util
        global download_start_date_string
        global download_end_date_string
        global download_end_date_util

        global start_date_string
        global start_date_util 
        global end_date_string 
        global end_date_util 

        current_selected_date = cal.selection_get() #this returns a date time object
        #depending on type, change accordingly
        if type =="start": #if start #first set for data processing
            #update backend variables
            start_date_util = current_selected_date
            start_date_string = get_date_util_string(current_selected_date)
            #update the visual labels on the main root
            start_date_label.config(text = start_date_string)
            toplevel.destroy()  # Close the popup
        elif type =="end": #update end date
            #update backend variables
            end_date_util = current_selected_date
            end_date_string = get_date_util_string(current_selected_date)
            #update the visual labels on the main root
            end_date_label.config(text = end_date_string)
            toplevel.destroy()  # Close the popup
        elif type =="series":
            date_list_util.append(current_selected_date) #make sure to append to both. such that indeces match one to one
            date_list_util.sort() #sort the list in chronological order
            listbox.delete(0, tkinter.END)#delete all dates in box
            for date in date_list_util:
                listbox.insert(tkinter.END, get_date_util_string(date))#re-add in sorted form
        elif type == "get start": #updated downloaidng variables
            #update backend variables
            download_start_date_util = current_selected_date
            download_start_date_string = get_date_util_string(current_selected_date)
            #update the visual labels on the main root
            download_start_date_label.config(text = download_start_date_string)
            toplevel.destroy()  # Close the popup
        elif type == "get end": #updated downloaidng variables
            #update backend variables
            download_end_date_util = current_selected_date
            download_end_date_string = get_date_util_string(current_selected_date)
            #update the visual labels on the main root
            download_end_date_label.config(text = download_end_date_string)
            toplevel.destroy()  # Close the popup
        elif type =="get series":
            download_date_list_util.append(current_selected_date) #make sure to append to both. such that indeces match one to one
            download_date_list_util.sort() #sort the list in chronological order
            download_datelist_listbox.delete(0, tkinter.END) #delete all dates in box
            for date in download_date_list_util:
                download_datelist_listbox.insert(tkinter.END, get_date_util_string(date))#re-add in sorted form

    #create a label in the popup to show the current selected date
    tkinter.Label(toplevel, text = "Selected Date:")
    selected_date_label = tkinter.Label(toplevel, text= str(current_selected_date))
    selected_date_label.pack(pady=5)
    add_selection_btn = tkinter.Button(toplevel, text="Add Selection", command=add_selected_date)
    add_selection_btn.pack(pady=5)

    #continuously update the selected date in hte popup
    def show_selected_date():
        selected_date = cal.selection_get()
        selected_date_label.config(text=f"Selected Date: {selected_date}")
        toplevel.after(100, show_selected_date)  # Refresh every 500 milliseconds (0.5 seconds)
    # Start the continuous update loop
    show_selected_date()

'''
Function to reset the dates to none
#INPUT: the date type to set to None
#OUTPUT: sets selected date to None
'''
def reset_date(type):
    #make clear global variables will change 
    global start_date_string
    global start_date_util 
    global end_date_string 
    global end_date_util 

    if type == "start":
        start_date_util = None
        start_date_string = None
        start_date_label.config(text = "None")
    elif type == "end":
        end_date_util = None
        end_date_string = None
        end_date_label.config(text = "None")
    
'''
Deletes selected date from the DOWNLOAD DATA listbox and the dateslilst on the backend
#INPUT: list of indedces, list of indeces to delete from the list box
#OUTPUT: deletes chosen dates
'''
#smae function but for the listbox for the downloading data selection
def download_delete_from_series(list_of_indeces):
    for index in sorted(list_of_indeces, reverse=True):
        download_datelist_listbox.delete(index)
        # Remove from date_list using the same index
        del download_date_list_util[index]
    print("Dates to download left", download_date_list_util)

'''
Deletes selected date from the processing listbox and the dateslilst on the backend
#INPUT: list of indedces, list of indeces to delete from the list box
#OUTPUT: deletes chosen dates
'''
def delete_from_series(list_of_indeces):
    for index in sorted(list_of_indeces, reverse=True):
            listbox.delete(index)
            # Remove from date_list using the same index
            del date_list_util[index]
    print("Dates left", date_list_util)

'''
Searches and retrieves the list of the custom shape files that have been saved
uses a set directory organization
#OUTPUT: list of strings of the custom regions that have been defined, without their file endings
'''
def get_custom_region_names():
    names_list = []
    directory = os.path.join(parent_dir, "maps", "custom_polygons")#get directory of where the custom files are
    files_list = os.listdir(directory)
    for file_name in files_list: #for all the names
        if file_name.endswith(".shp"): #only keep .shp names
            file_name_parts = file_name.split(".")
            names_list.append(file_name_parts[0]) #save first part which is the name
    return names_list #send back list

#---------------------------------DOWNLOADING DATA FIELDS---------------------------------------------------------
#---------------------Date picker for Downloading data 
ttk.Label(get_data_frame, text="DOWNLOAD ADS-B DATA", font = ("garamond", 14, "italic", "bold")).grid(column = 1, row = 0, columnspan = 2, sticky = 'n')
ttk.Label(get_data_frame, text="What timeframe would you like to download data for?",  wraplength=175, justify='center', background = 'lightblue').grid(column=0, row=0)
#add button to get calendar popups - use lambda to pass function and arguments for when clicked
#for start date
ttk.Button(get_data_frame, text="Select", command=lambda: open_calendar_popup("get start")).grid(column=2, row=1, sticky='w')
#ttk.Button(get_data_frame, text="Reset", command=lambda: reset_date("get start")).grid(column=3, row=1, sticky='w')
#for end date
ttk.Button(get_data_frame, text="Select", command=lambda: open_calendar_popup("get end")).grid(column=2, row=2, sticky='w')
#ttk.Button(get_data_frame, text="Reset", command=lambda: reset_date("get end")).grid(column=3, row=2, sticky='w')

#---------------create list box for the date array selection for downloading data
#add the checks next to the dates selected
get_data_start_ticker = tkinter.IntVar() #var will be zero if not checked, 1 if checked. use var.get() to get values
tkinter.Checkbutton(get_data_frame, text="Start Date", variable=get_data_start_ticker).grid(row=1, column = 0, sticky= 'w')
get_data_end_ticker = tkinter.IntVar()
tkinter.Checkbutton(get_data_frame, text="End Date", variable=get_data_end_ticker).grid(row=2, column = 0, sticky= 'w')
get_data_list_ticker = tkinter.IntVar()
tkinter.Checkbutton(get_data_frame, text="Date Series", variable=get_data_list_ticker).grid(row=3, column = 0, sticky= 'w')

# Button to open the calendar popup
download_add_date_to_series_button = ttk.Button(get_data_frame, text="Add Date to Series", command=lambda: open_calendar_popup("get series")).grid(column=1, row=4, sticky='nwe')
# Listbox to show added dates
download_datelist_listbox = tkinter.Listbox(get_data_frame, height=5, selectmode=tkinter.MULTIPLE)
download_datelist_listbox.grid(column = 1, row = 3)
# Button to delete selected dates from listbox and list
delete_button = ttk.Button(get_data_frame, text="Delete Selected Date(s)", command=lambda: download_delete_from_series(list(download_datelist_listbox.curselection()))).grid(column = 1, row = 5, sticky ='nwe')

#sampling rate dropdown 
tkinter.Label(get_data_frame, text="Sampling rate (min):").grid(column = 0, row =6, sticky= 'w') 
sampling_rate_options = [5, 10, 20, 30, 60]
sampling_combo_box = ttk.Combobox(get_data_frame, values= sampling_rate_options)
sampling_combo_box.grid(column = 1, row = 6, sticky= 'w') #combobox


#-----------------------Call download data button--------------------------------------
'''
Using user inputs, download specified data
'''
def call_download_script():
    start = None if get_data_start_ticker.get() == 0 else download_start_date_util
    end = None if get_data_end_ticker.get() == 0 else download_end_date_util
    series = None if get_data_list_ticker.get() == 0 else download_date_list_util

    #set sampling rate to None if blank (default at index = -1) is selected, otherwise use selectd index to grab selected value from options
    sampling_rate = None if sampling_combo_box.current() == -1 else sampling_rate_options[sampling_combo_box.current()] 
    
    get_ADS_B_data.main(start, end, series, sampling_rate)

#get data button
tkinter.Button(get_data_frame, text = "Download", font = ("garamond", 14, "italic", "bold"), background = "firebrick1", command = call_download_script).grid(column = 2, row = 6, columnspan = 1, sticky="nwse")
#--------------------------------END DOWNLOADING DATA FIELDS-----------------------------------------------------------


#---------------------------------DATA PROCESSING FIELDS----------------------------------------------------------------
#------------------start and end date selections - Add label to select what to input
ttk.Label(process_data_frame, text="PROCESS ADS-B DATA", font = ("garamond", 14, "italic", "bold")).grid(column = 1, row = 0, columnspan = 2, sticky = 'n')
ttk.Label(process_data_frame, text="What timeframe would you like to process?",  wraplength=175, justify='center', background = 'lightblue').grid(column=0, row=0, sticky='nwe')
#add button to get calendar popups - use lambda to pass function and arguments for when clicked
#for start date
ttk.Button(process_data_frame, text="Select", command=lambda: open_calendar_popup("start")).grid(column=2, row=1, sticky='w')
#ttk.Button(process_data_frame, text="Reset", command=lambda: reset_date("start")).grid(column=3, row=1, sticky='w')
#for end date
ttk.Button(process_data_frame, text="Select", command=lambda: open_calendar_popup("end")).grid(column=2, row=2, sticky='w')
#ttk.Button(process_data_frame, text="Reset", command=lambda: reset_date("end")).grid(column=3, row=2, sticky='w')

#---------------create list box for the date array selection for processing
#add the checks next to the dates selected
start_date_ticker = tkinter.IntVar() #var will be zero if not checked, 1 if checked. use var.get() to get values
tkinter.Checkbutton(process_data_frame, text="Start Date", variable=start_date_ticker).grid(row=1, column = 0, sticky= 'w')
end_date_ticker= tkinter.IntVar()
tkinter.Checkbutton(process_data_frame, text="End Date", variable=end_date_ticker).grid(row=2, column = 0, sticky= 'w')
date_series_ticker = tkinter.IntVar()
tkinter.Checkbutton(process_data_frame, text="Date Series", variable=date_series_ticker).grid(row=3, column = 0, sticky= 'w')

# Button to open the calendar popup
add_date_to_series_button = ttk.Button(process_data_frame, text="Add Date to Series", command=lambda: open_calendar_popup("series")).grid(column=1, row=4, sticky='nwe')
# Listbox to show added dates
listbox = tkinter.Listbox(process_data_frame, height=5, selectmode=tkinter.MULTIPLE)
listbox.grid(column = 1, row = 3)
# Button to delete selected dates from listbox and list
delete_button = ttk.Button(process_data_frame, text="Delete Selected Date(s)", command=lambda: delete_from_series(list(listbox.curselection()))).grid(column = 1, row = 5, sticky ='nwe')

#---------------------------END DATE PROCESSING FIELDS----------------------------------------------------------------------------------

#-------------------------------custom region picking 
#create region picking area 
ttk.Label(process_data_frame, text="What region?", justify='center', background = 'lightblue').grid(column=0, row=6, sticky='nwe')
#for the whole world
world_ticker = tkinter.IntVar()
tkinter.Checkbutton(process_data_frame, text="Whole World", variable=world_ticker).grid(column = 0, row =7, sticky='w') 
#for specified region
region_ticker = tkinter.IntVar()
tkinter.Checkbutton(process_data_frame, text="Preset Region:", variable=region_ticker).grid(column = 0, row =8, sticky= 'w') 
preset_combo_box = ttk.Combobox(process_data_frame, values=admin_list)
preset_combo_box.grid(column = 1, row = 8, sticky= 'w') #combobox
#now for the custom region
custom_region_ticker = tkinter.IntVar()
tkinter.Checkbutton(process_data_frame, text="Custom Region:", variable=custom_region_ticker).grid(column = 0, row =9, sticky='nw')
custom_region_names = get_custom_region_names()
custom_combo_box = ttk.Combobox(process_data_frame, values=custom_region_names) #combobox
custom_combo_box.grid(column = 1, row =9, sticky= 'nw') 

#--------------------NIC bins---------------------
ttk.Label(process_data_frame, text="NIC Bin Edges", justify='center', background = 'lightblue').grid(column=0, row=10, sticky='nwe')
current_bins_label = ttk.Label(process_data_frame, text="Current selection: ", justify='center')
current_bins_label.grid(column=0, row=11, sticky='nwe')
bins_input_text = tkinter.Text(process_data_frame, height = 5, width = 16)
bins_input_text.grid(column = 1, row = 11)

#frame for colors
#make frame for colors
colors_frame = tkinter.Frame(process_data_frame, relief="groove", borderwidth=3)
colors_frame.grid(column = 2, row = 11, sticky = 'nwe')  #create frame for the get data frame

'''
Function to update what the current selection for the NIC bins is
#INPUT: bins_text, string, takes in what is in the text field upon clicking the update button
        label, the tkk.Label instance for the label
#OUTPUT: updates the selection
'''
def update_bins(bins_text):
    bin_edges = bins_text.split(",")

    global NIC_bin_edges 
    NIC_bin_edges = [] #empty out edges array from it had values from before
    global NIC_colors_hex_list 

    #format the given bin edges to only keep number or inf
    for edge in bin_edges:
        edge = edge.replace(" ", "")#get rid of any spaces if there are any in the edge
        try:
            if edge == "inf":
                edge = float("inf")#if is inf in string form, change to a float 
            else:#otherwise we have a number
                edge = float(edge) #change to float 
        except:
            raise ValueError("Invalid types entered for NIC edges. Either type in numbers or 'inf' for infinity sperated by commas. \n")
        
        NIC_bin_edges.append(edge)#append to the NIC bin edges array
    
    #check to make sure lower bound is less than its upper bound
    for i in range(len(NIC_bin_edges)-1):
        if NIC_bin_edges[i] >= NIC_bin_edges[i+1]: #alert user if rule is broken
            raise ValueError("You cannot input a bin that has a lower bound equal or grater than its upper bound")
    
    display_array = [] #array to hold the acutal bins to display to the user, is a list of "(X, X]" intervals as strings
    num_bins = len(NIC_bin_edges)-1 #the actual number of bins. one less than the edges 
    for i in range(0, num_bins): #this will go to one less than the num_bins startint with 1
        display_array.append("(" + str(NIC_bin_edges[i])  + ", " + str(NIC_bin_edges[i+1]) + "]")
    current_bins_label.config(text = "Current bins selection: \n" + ", ".join(display_array),  wraplength=175)

    #------------Color selection
    # Store selected colors
    NIC_colors_hex_list = ["#FFFFFF"] * len(display_array)  # Default tto a full list of white
    color_boxes = []  # Store references (the labels that are the boxes themselves) to color box widgets

    '''
    Choose colors
    #INPUT: index, int of the index of the label
    #OUTPUT: add updated color to the list, change box to reflect color
    '''
    def choose_color(index):
        color = colorchooser.askcolor()[1]  # Get hex color
        if color:  # If user selects a color
            color_boxes[index].config(bg=color)
            NIC_colors_hex_list[index] = color
        
    #now that label is updated, lets add labels for the user to select colors 
    for item in colors_frame.winfo_children(): #get rid of previous labels 
        item.destroy()

    # This section from CHAT GPT:  Create UI elements
    for i, label in enumerate(display_array): 
        tkinter.Label(colors_frame, text=label).grid(column=0, row=i, sticky='nwe')

        btn = tkinter.Button(colors_frame, text="Choose Color", command=lambda i=i: choose_color(i), padx=8)
        btn.grid(column=1, row=i, sticky='nwe')

        color_box = tkinter.Label(colors_frame, width=2, height=2, bg=NIC_colors_hex_list[i], relief="solid", bd=1, padx=8)
        color_box.grid(column=2, row=i, sticky='nwe')

        color_boxes.append(color_box)
#End update bins

update_bins_button = ttk.Button(process_data_frame, text="Update NIC bin edges", command=lambda: update_bins(bins_input_text.get(1.0, "end-1c"))).grid(column = 1, row = 12, sticky ='nwe')
#---------End NIC Bins--------------------------------


#-----------------------call processing button--------------------------
'''
Call the data processing script with the given parameters
'''
def call_processing_script(): 
    start = None if start_date_ticker.get() == 0 else start_date_util
    end = None if end_date_ticker.get() == 0 else end_date_util
    series = None if date_series_ticker.get() == 0 else date_list_util
    
    world = 0 if world_ticker.get() == 0 else 1 #treat world as a boolean
    #preset region set vars to pass
    region = None #add if statemetns for the -1 case
    if region_ticker.get() == 0:  #if not ticked
        region = None #set to none
    else: #if ticked
        selected_index = preset_combo_box.current() #get index
        if selected_index != -1: #only update if something is selected - -1 means nothing
            region = admin_list[selected_index] #a region has been selected, update
    #custom region set vars to pass
    custom = None 
    if custom_region_ticker.get() == 0: #if not ticked
        custom = None #set to none
    else: #if ticked
        selected_index = custom_combo_box.current() #get index
        if selected_index != -1: #only update if something is selected - -1 means nothing
            custom = custom_region_names[selected_index] #a custom region has been selected, update

    #call main on data processing with passed variables
    process_ADS_B_data.main(start, end, series,  world, region, custom, NIC_bin_edges, NIC_colors_hex_list)
    

#button to run processing
tkinter.Button(process_data_frame, text = "Process Data", font = ("garamond", 14, "italic", "bold"), background = "limegreen", command = call_processing_script).grid(column = 2, row = 12, sticky="nwse")
#-----------------End processing button

#run the widget
root_window.mainloop()

