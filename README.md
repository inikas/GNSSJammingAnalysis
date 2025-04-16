# GNSSJamming
Quantify frequency and strength of GNSS jamming affecting commercial aircraft across the globe.

<!-- Hidden comment: note that the markdown anchors are just the name in all lowercase and spaces replaced with dashes -->
## Table of Contents
- [Introduction to GNSS Jamming](#introduction-to-gnss-jamming)
- [Installation](#installation)
- [Tool Overview](#toool-overview)
- [GUI Interaction](#gui-interaction)
- [Outputs](#outputs)
- [Next Steps](#next-steps)
- [Appendix](#appendix)


## Introduction to GNSS Jamming
Global Navigation Satellites Systems (GNSS), which the American Global Positioning System (GPS) is an example of, are used by private, commercial, and military users for accurate and precise location services. The signals emitted by GNSS satellite systems are used by both terrestrial and airbornes systems, such as aircraft. Notably, however, history was made on March 3, 2025 "when the [Lunar GNSS Receiver Experiment (LuGRE)](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/nasa-successfully-acquires-gps-signals-on-moon/#:~:text=NASA%20and%20the%20Italian%20Space,signals%20on%20the%20Moon's%20surface.) became the first technology demonstration to acquire and track Earth-based navigation signals on the Moon’s surface." GNSS signals are [used](https://www.gps.gov/applications/) by devices ranging from cell phones to shipping containers. Diruption of these capacilities to such assets could lead to significant inconvenience and economic loss. Disruption of GNSS signals to systems like commercial aircraft, however, [could aversly affect thier safety systems](https://www.csis.org/events/what-are-impacts-gps-jamming-and-spoofing-civilians), making routine flying more dangerous. 

As GNSS systems are space systems, attacks that disrupt or corrupt GNSS signals can be considered counterspace capabilities. Jamming, ["an electronic attack that uses radio frequency signals to interfere with communications,"](https://aerospace.csis.org/aerospace101/counterspace-weapons-101/) is increasinlgy being used to target GNSS signals. Interactive maps like [gpsjam.org](https://gpsjam.org/) can be used to view the extent of such jamming. Aditionally, as coverage of commercial aircraft is widespread, observing jamming instances on commercial aircraft can give significant insight into GNSS jamming over an area, more generally.

## Tool Overview
While an intern with the [Aerospace Security Project at the Center for Strategic and International Studies](https://www.csis.org/programs/aerospace-security-project) in Washington, D.C., I explored such tools but I could not find an open source tool that quantified jamming over time. 

This project is an attempt to allow the user to more clearly grasp the number and strength of jamming instances over time and over a particular area. To do this, I used publicly avaiable Automatic Dependent Surveillance–Broadcast (ADS-B) from [ADS-B Exchange](https://www.adsbexchange.com/) that includes aircraft positional and GNSS system integrity data. Specifically, the Navigation Integirty Category (NIC) is used to determine whether or not jamming is occuring. The user can define buckets to group data in, but generally, a $NIC >= 7$ implies normal conditions, and $NIC <=6$ likely (although not necessarily) implies jamming. Note that this parameter gives information on the precision of the location extracted from the GNSS signals rather than accuracy which could give insight into whether or not spoofing is ocurring. 

Table 1, below, shows the different NIC values (always integers) and the associated level of confidence in the reading, expressed by the Radius of Containment ($R_c$); the $R_c$ parameter describes the radius of a circle centerd at the aircraft's reported position in which the actual location of the aircraft has a $99.999$% of being within. For more information on ADS-B, you can refer to this [Overview of Automatic Dependent Surveillance-Broadcast (ADS-B) Out](https://www.icao.int/NACC/Documents/Meetings/2021/ADSB/P01-OverviewADSBOut-ENG.pdf) published by the International Civil Aviation Organization (ICAO).

 **Table 1:** NIC value and corresponding size of containment radius. Source: Zixi Liu, Sherman Lo, and Todd Walter, "GNSS Interference Source Localization Using ADS-B data," Stanford University, [https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Liu_ION_ITM_2022_ADSB.pdf](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Liu_ION_ITM_2022_ADSB.pdf).</p>

<img width="261" alt="image" src="https://github.com/user-attachments/assets/de9dcf69-565b-4c07-95d1-af5e71523701" />

## Installation
Downloading the repository, you will see the following file structure: 

```
📁 .
├── 📁 ADS_B_Data
├── 📁 code
│   ├── countries_list.pkl
│   ├── get_ADS_B_data.py
│   ├── jamming_dashboard.py
│   ├── package_install_check.py
│   ├── process_ADS_B_data.py
├── 📁 maps
│   ├── 📁 custom_polygons
│   ├── 📁 ne_10m_admin_0_countries
│   ├── (global map files ...)
└── 📁 outputs
```
This repository is coded using Python, and works for both Mac and Windows operating systems. Make sure you have all necessary packages. The list of packages that you will need that are not included in the standard Python library are:
```
1. tkcalendar
2. python-dateutil
3. pandas
4. geopandas
5. requests
6. beautifulsoup4  
7. numpy
8. matplotlib
9. folium
10. mplcursors
```
You can either run the `pip3 install [package name]` command in the terminal to individually install each package, or you can open and run the `package_install_check.py` script that will automatically check and install missing packages. 

To use the tool, open and run `jamming_dashboard.py`. This will open the main Graphical User Interface (GUI).

## GUI Interaction 
Open and run the `jamming_dashboard.py` file to launch the GUI. The GUI is broken into two sections, as follows:

1. _Downloading ADS-B Data_

This section of the GUI is used to download the ADS-B data from the web. Currently, this is done by downloading data from the [ADS-B Exchange historical data](https://www.adsbexchange.com/products/historical-data/). This website publishes free, historical data for every first day of the month, found under the “readsb-hist” section. Data is oriignally stored in a JSON format. When it is downloaded, it is cleaned and stored into a [GeoDataFrame](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html). 

To download data, you can either select a single start date, a start and end date that will cover every day between and including the start and end bounds, or a series of dates of your choosing. Aditionally, a sampling rate that prescribes how often to sample data from the repository in minutes is needed. When ready, click the _Download_ button, which will save the data into organized files within the _ADS_B_Data_ folder. When this is done, you will see a folder for each day that has a file for each time you have sampled - the file names will take the form of _000000Z.pkl_. The first two digits represent the hour, the middle two the minutes, and the last two the seconds. The "Z" represents Zulu time. A sample of what we start with and end with for Januaary 1, 2024 at 00:00:00Z is included below in Table 2:

**Table 2:** The left shows sample data for a single flight at 00:00:00Z on January 1, 2024. Each time file on ADS-B Exchange has thousands of these entires corresponding to each flight airborne and sending out ADS-B signals at the time. The right shows how it is downloaded in the tool; note that each flight now takes a single row in the GeoDataFrame. 

<img width="989" alt="image" src="https://github.com/user-attachments/assets/6c606936-f240-43cb-a3ba-4090a73718dc" />

Note:
- When downloading, observations from that data that have $NIC = 0$ are thrown out. 
- If you are downloading to a folder that is stored in the cloud, say a OneDrive folder, downloading may take some time as your system tries to simultenosuly sync ot the cloud. To avoid this, you can download to a local folder or turn off syncing to the cloud until your download is complete.
- On data size: at a sampling rate of 30 min, a typically day may store between $10-20$ MB of data.


2. _Processing ADS-B Data_

This section is to be used after data is downloaded. It contains date options in the same was as the download data section. The user can only process data for files that have already ben downloaded. In this section, the user is also asked to choose a region of interest to process over. One can either choose the whole world, one of the predefined regions, or a custom region. To make a custom region, refer to the Appendix below. After custom regions are created in the *custom_regions folder*, they are automatically shown in the dropdown menu in the GUI. The tool comes with three preloaded custom regions as follows: 

1. East Med
2. Black Sea
3. Baltic

![Default Custom Regions](https://github.com/user-attachments/assets/3d4e4af8-c0ce-4309-826f-9e2d48f28f5a)

NIC bin edges also need to be defined by the user. These edges define the buckets that the program will group observations in. You can only input integers, floats, or the string *'inf,'* all seperated by commas in this field. For example, if you are interested in looking at observations below the $NIC >= 7$ threshold and above, that correspond to jamming and no jamming, respectively, you can enter *0, 6, 'inf'*. Once you type the bin edges in the text field, make sure to click on the _Update NIC bin edges_ button. Upon clicking this button, you will see your changes notes in the _Current Selection_ field. Note that the lower bounds are exlusive and the upper bound inclusive. You will also see a color popup appear. By default, all bins will be assigned white, but specifying colors will make it easier to differentiate quantities later on in the outputted plots. 

When all user inputs are complete, click the _Process Data_ button. It may take some time to process and display the outputs. 

## Outputs
This tool outputs a set of graphs and maps. Table 3 describes the graph outputs, and Table 4 the map outputs for a test run over Poland on January 1, 2024. 

**Table 3:** The left set of plots organizes every single sample collected into the prescribed bins. The top left shows all samples organized into the bins, and the bottom left shows the percentage of each group with respect to the total contained in all the bins. The right set of plots shows the number of unique flights that fell into each bin. The top shows the number of flights and the bottom the percentage of flights in each bin, again with respect to the total number of unique flight numbers in the bins defined by the user. Note that if a flight expereinced a NIC value in more than one bin over time it will be included in both on the top, but it will not be double counted when calculating the percentage (i.e. the percentage value in the bottom graph is not necessarily the height of each bin on the top divided by the total height of the full graph). Also, note that the popups that appear when hovering over the graphs display data for the bin highlighted by the user's mouse. 

<img width="997" alt="image" src="https://github.com/user-attachments/assets/596d189b-2dd6-430f-84e0-b454124c9f23" />

**Table 4:** The tool also creates a map of the data - **only the first day is saved if mulptile dates for analyssi are chosen**. The map on the left, saved to _map_raw.html_ in the `Outputs` folder is a map of every data point. The right shows the map saved in `map_averaged.html`, which averages the samples over cells and plots a single point at the center of the cells. The size of the cells can be manually changed within `process_ADS_B_data.py` inside the *get_NIC_data_boxed_averages()* function by changing the *lat_bin_size* and *long_bin_size* that define the cell dimensions. Note the filters on the left that allow you to show or hide data within a particualar bin. Click a point to get more information about it. 

<p align="center">
  <img src="https://github.com/user-attachments/assets/f089d913-3a3a-425e-89d0-6ac0ec1425eb" width="49%" />
  <img src="https://github.com/user-attachments/assets/62f9774f-364c-4971-999f-aa36e7780da1" width="49%" />
</p>

While the maps save to the output folder, one can have them automatically open by uncommenting the *webbrowser.open* lines within `process_ADS_B_data.py`.

## Next Steps
1. The tool currently parses the web for data, but an [rclone](https://developers.cloudflare.com/r2/examples/rclone/) can be used to interact with ADS-B exchange. Also refer to ADS-B Exchange on how to [pull data from their buckets.](https://www.adsbexchange.com/pull-data/).
2. The data shown in the graphs is not saved. If you would like to save that data in a dataframe 9or whatever form of your choosing), you can do so by saving the $counts_stats$ (left two plots) and the $flight_stats$ (right two plots) variables at the end of the `process_ADS_B_data.py` file.
 
## Appendix

Follow this tutorial to add custom regions. You will need to have QGIS, a free geogrpahic information system application, downloaded - I recommend the [QGIS 3.34 Long Term Release (LTR)](https://qgis.org/download/).
1. Open the `QGIS_Custom_Polygons.qgz` file in the *maps/custom_polygons* folder. You should see the three custom layers present on a map of the world
2. Click the *New Shape File Layer...* button: ![image](https://github.com/user-attachments/assets/23bcb964-d695-47b4-801f-7a1f904349d4)
3. In the window that appears, enter a *File Name*. This will be the name that appears in the dropdown in the GUI. Also set the *Geometry Type* to *Polygon*. Your window should look something like this: ![image](https://github.com/user-attachments/assets/9d425228-5c5a-47d8-bc0d-a9d45293d48d)
4. Click *OK*.
5. Your new layer will appear in the *Layers* tab in the bootm left of the screen. Right click on your layer and select *Toggle Editing*:
![image](https://github.com/user-attachments/assets/c8813a0a-6220-41a8-88f9-5c58c19b1f4c)
6. Then click the *Add Polygon Feature* button in the toolbar: ![image](https://github.com/user-attachments/assets/b539290d-a137-4cc3-b14b-1b07c944f041).
You can now begin drawing your custom region by moving your mouse and left-clicking to drop vertices on your polygon. Here is an example of what the drawing process looks like: ![image](https://github.com/user-attachments/assets/814f3e0f-c417-48ea-a0f8-86e0e0c80be6)
7. Make sure to close your polygon at the end, and righ-click to stop drawing. When you right-click, a text window will popup asking for an *id*.

![image](https://github.com/user-attachments/assets/850c1b21-f237-45b7-8f6d-507d98fa9522)

Enter an integer; this will be a reference to your layer that can be displayed using the *Show Labels* option in the edit layer tab (when you right-click or double-click your layer in the bottom left). Click *OK*.

9. Untoggle "Toggle editing* in the layer options - it should not appear grayed out. Make sure TO SAVE.

After saving, your shape layer will be saved in the *custom_polygons* folder, and it will automatically appear in the GUI when you re-load (re-run) it.



