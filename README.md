# Carpool Canada rideshare automation script #

Web scraping script developed for - [https://www.carpoolworld.com/](https://www.carpoolworld.com/) using Python 2.7 and BeautifulSoup.


## Module Requirements :

> Python  - 2.7.10 , 
> BeautifulSoup 


## Installing module dependencies :

* Download and install Python -  [Python download](https://www.python.org/downloads/)

* Install BeautifulSoup-3 using below command  - 
```
sudo pip install BeautifulSoup
```


### Running the script :

* Open terminal and move to project folder by using command -
```
cd /path/to/script/
```
* After that run script using below command -
```
python carpool_scraper.py
```


### Verifying script Output :

* All scraped data is update into **carpool_data_canada** table with given fields - ['from_stop','to_stop','performer','schedule','gender','Smoking_habits','Seat_type']

		

### Checking for Errors 

* All script logs (error/info) data will be updated into **scraping_logs/module.log** file



### Sample RUN :

