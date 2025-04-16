#Ioannis P. Nikas. April 2025. For the Aerospace Security Project at CSIS in Washington, D.C.
#Written with occasional help from Chat GPT from OpenAI
#This script checks if you have all the packages for the jamming tool downloaded or not

#With help from Chat GPT:
import subprocess
import sys 

#this list is just a collection of all the packages that ARE NOT INCLUDED in the standard Python library used in the other scripts
packages_list = ["tkcalendar", 
 "python-dateutil", 
 "pandas", 
 "geopandas", 
 "requests", 
 "bs4", 
 "numpy",
 "matplotlib",
 "folium", 
 "mplcursors"]


#run through and check if each package is installed or not
for pkg in packages_list:
    result = subprocess.run(['pip', 'show', pkg], stdout=subprocess.DEVNULL)
    if result.returncode == 0:
        print(f"{pkg} is installed ✅")
    else:
        print(f"{pkg} is NOT installed ❌. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])



