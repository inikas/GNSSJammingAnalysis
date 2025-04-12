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
While an intern with the [Aerospace Security Project at the Center for Strategic and International Studies](https://www.csis.org/programs/aerospace-security-project) in Washington, D.C., I explored such tools but I could not find an open source tool that quantified jamming over time. This project is an attempt to allow the user to more clearly grasp the number and strength of jamming instances over time and over a particular area. To do this, I used publicly avaiable Automatic Dependent Surveillance–Broadcast (ADS-B) from [ADS-B Exchange](https://www.adsbexchange.com/) that includes positional and GNSS system integrity data. Specifically, the Navigation Integirty Category (NIC) is used to determine whether or not jamming is occuring. The user can define buckets to group data in, but generally, a $NIC >= 7$ implies normal conditions, and $NIC <=6$ likely (although not necessarily) implies jamming. Note that this parameter gives information on the precision of the location extracted from the GNSS signals rather than accuracy which could give insight into whether or not spoofing is ocurring. Table 1, below, shows the different NIC values (always integers) and the associated level of confidence in the reading, expressed by the Radius of Containment ($R_c$); the $R_c$ parameter describes the radius of a circle centerd at the aircraft's reported position in which the actual location of the aircraft has a $99.999$% of being within. 

**Table 1:** NIC value and corresponding size of containment radius (Source: Zixi Liu, Sherman Lo, and Todd Walter, "GNSS Interference Source Localization Using ADS-B data," Stanford University, [https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Liu_ION_ITM_2022_ADSB.pdf](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Liu_ION_ITM_2022_ADSB.pdf).)

<img width="261" alt="image" src="https://github.com/user-attachments/assets/de9dcf69-565b-4c07-95d1-af5e71523701" />

## Installation
Downloading the repository, you will see the following file structure: 

```
📁 .
├── 📁 ADS_B_Data
│   ├── 📁 Reference Files	
│   ├── 📁 SNL Downloads
│   ├── 📁 Daily Analysis
│   └── 📁 Historical Analysis
└── 📁 Code
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

To use the tool, open and run `jamming_dashboard.py`. This will open the main GUI.

## GUI Interaction 
The GUI is broken into two sections, as follows:

1. _Downloading ADS-B Data_

ss
- zeros are killed
- what we start with, what we get
- - note delay may ocure if downloading to cloud folder


2. _Processing ADS-B Data_
- go through fields

- 



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
