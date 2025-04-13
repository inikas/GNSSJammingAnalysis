# GNSSJamming
Quantify frequency and strength of GNSS jamming affecting commercial aircraft across the globe.

<!-- Hidden comment: note that the markdown anchors are just the name in all lowercase and spaces replaced with dashes -->
## Table of Contents
- [Introduction to GNSS Jamming](#introduction-to-gnss-jamming)
- [Installation](#installation)
- [Overview](#overview)
- [GUI Interaction](#gui-interaction)
- [Outputs](#outputs)
- [Next Steps](#next-steps)


## Introduction to GNSS Jamming
Global Navigation Satellites Systems (GNSS), which the American Global Positioning System (GPS) is an example of, are used by private, commercial, and military users for accurate and precise location services. The signals emitted by GNSS satellite systems are used by both terrestrial and airbornes systems, such as aircraft. Notably, however, history was made on March 3, 2025 "when the [Lunar GNSS Receiver Experiment (LuGRE)](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/nasa-successfully-acquires-gps-signals-on-moon/#:~:text=NASA%20and%20the%20Italian%20Space,signals%20on%20the%20Moon's%20surface.) became the first technology demonstration to acquire and track Earth-based navigation signals on the Moon’s surface." GNSS signals are [used](https://www.gps.gov/applications/) by devices ranging from cell phones to shipping containers. Diruption of these capacilities to such assets could lead to significant inconvenience and economic loss. Disruption of GNSS signals to systems like commercial aircraft, however, [could aversly affect thier safety systems](https://www.csis.org/events/what-are-impacts-gps-jamming-and-spoofing-civilians), making routine flying more dangerous. 

As GNSS systems are space systems, attacks that disrupt or corrupt GNSS signals can be considered counterspace capabilities. Jamming, ["an electronic attack that uses radio frequency signals to interfere with communications,"](https://aerospace.csis.org/aerospace101/counterspace-weapons-101/) is increasinlgy being used to target GNSS signals. Interactive maps like [gpsjam.org](https://gpsjam.org/) can be used to view the extent of such jamming. Aditionally, as coverage of commercial aircraft is widespread, observing jamming instances on commercial aircraft can give significant insight into GNSS jamming over an area, more generally.

## Overview
While an intern with the [Aerospace Security Project at the Center for Strategic and International Studies](https://www.csis.org/programs/aerospace-security-project) in Washington, D.C., I explored such tools but I could not find an open source tool that quantified jamming over time. 

This project is an attempt to allow the user to more clearly grasp the number and strength of jamming instances over time and over a particular area. To do this, I used publicly avaiable Automatic Dependent Surveillance–Broadcast (ADS-B) from [ADS-B Exchange](https://www.adsbexchange.com/) that includes aircraft positional and GNSS system integrity data. Specifically, the Navigation Integirty Category (NIC) is used to determine whether or not jamming is occuring. The user can define buckets to group data in, but generally, a $NIC >= 7$ implies normal conditions, and $NIC <=6$ likely (although not necessarily) implies jamming. Note that this parameter gives information on the precision of the location extracted from the GNSS signals rather than accuracy which could give insight into whether or not spoofing is ocurring. Table 1, below, shows the different NIC values (always integers) and the associated level of confidence in the reading, expressed by the Radius of Containment ($R_c$); the $R_c$ parameter describes the radius of a circle centerd at the aircraft's reported position in which the actual location of the aircraft has a $99.999$% of being within. For more information on ADS-B, you can refer to this [Overview of Automatic Dependent Surveillance-Broadcast (ADS-B) Out](https://www.icao.int/NACC/Documents/Meetings/2021/ADSB/P01-OverviewADSBOut-ENG.pdf) publiidhed by the International Civil Aviation Organization (ICAO).

**Table 1:** NIC value and corresponding size of containment radius. Source: Zixi Liu, Sherman Lo, and Todd Walter, "GNSS Interference Source Localization Using ADS-B data," Stanford University, [https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Liu_ION_ITM_2022_ADSB.pdf](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Liu_ION_ITM_2022_ADSB.pdf).

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
This repository is coded using Python. Make sure you have all necessary packages. The list of packages that you will need that are not included in the standard Python library are:
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
You can either run the `pip3 install [package name]` command to individually install each package, or you can open and run `package_install_check.py` script that will automatically check and install missing packages. 

To use the tool, open and run `jamming_dashboard.py`. This will open the main Graphical User Interface (GUI).

## GUI Interaction 
Open and run the `jamming_dashboard.py` file to launch the GUI. The GUI is broken into two sections, as follows:

1. _Downloading ADS-B Data_

This section of the GUI is used to download the ADS-B data from the web. Currently, this is done by downloading data from the [ADS-B Exchange historical data](https://www.adsbexchange.com/products/historical-data/). This website publishes free, historical data for every first day of the month, found under the “readsb-hist” section. Data is oriignally stored in a JSON format. When it is downloaded, it is cleaned and stored into a [GeoDataFrame](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html). 


To download data, you can either select a single start date, a start and end date that will cover every day between and including the start and end bounds, or a series of dates of your choosing. Aditionally, a sampling rate that prescribes how often to sample data from the repository in minutes is needed. When ready, click the _Download_ button, which will save the data into organized files within the _ADS_B_Data_ folder. When this is done, you will see a folder for each day that has a file for each time you have sampled - the file names will take the form of _000000Z.pkl_. The first two digits represent the hour, the middle two the minutes, and the last two the seconds. The "Z" represents Zulu time. A sample of what we start with and end with for Januaary 1, 2024 at 00:00:00Z is included below in Table 2:

Table 2: The left shows sample data for a single flight at 00:00:00Z on January 1, 2024. Each time file on ADS-B Exchange has thousands of these entires corresponding to each flight airborne and sending out ADS-B signals at the time. The right shows how it is downloaded in the tool; note that each flight now takes a single row in the GeoDataFrame. 

<img width="989" alt="image" src="https://github.com/user-attachments/assets/6c606936-f240-43cb-a3ba-4090a73718dc" />


**Note**
- When downloading, observations from that data that have $NIC = 0$ are thrown out. 
- If you are downloading to a folder that is stored in the cloud, say a OneDrive folder, downloading may take some time as your system tries to simultenosuly sync ot the cloud. To avoid this, you can download to a local folder or turn off syncing to the cloud until your download is complete.
- On data size: at a sampling rate of 30 min, a typically day may store between 10 -20 MB od data.


2. _Processing ADS-B Data_
- go through fields

  


Custom Regions:

## Outputs
- grpahs
- maps saved

## Next Steps
Assumptions: 
- will kill zeros
- note precentages for the graphs are only of the bins given .
- note map saving
- note can work for any OS
- Things that can be changed manually:
-   - note grid is preset but can be changed manually
-   - saving data frame with final data
 
To work on: 
- r2 and getting from the website itself
- need to re-add and clean up cusotm polygons
