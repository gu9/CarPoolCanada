import requests
from bs4 import BeautifulSoup
import random
import MySQLdb
import logging
import time


#
#Saving all error/warning logs to given file
#Change here for change in log filename or Log LEVEL
#
logging.basicConfig(filename='scraping_logs/module.log',level=logging.INFO)
logger = logging.getLogger('carpoolworld')


#Global variables used
url = 'https://www.carpoolworld.com/carpool_list_cities.html?country_code=CAN,CA&state_code=&start_at=1040&page_no='
header=['from_stop','to_stop','performer','schedule','gender','Smoking-habits','Seat_type']
fullSet=[]


#Use a random user-agent 
uaList=[
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Ubuntu/10.10 Chromium/8.0.552.237 Chrome/8.0.552.237 Safari/534.10',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36',
'Mozilla/5.0 (compatible; Origyn Web Browser; AmigaOS 4.0; U; en) AppleWebKit/531.0+ (KHTML, like Gecko, Safari/531.0+)',
'Mozilla/5.0 (compatible; Origyn Web Browser; AmigaOS 4.1; ppc; U; en) AppleWebKit/530.0+ (KHTML, like Gecko, Safari/530.0+)'
]


#MySQL connection
con = MySQLdb.connect(host="localhost",user="root",passwd="mushroom@123",db="carpool_data" ,charset='utf8')


#MySQL bulk insert all data
def insertBulkData():
  try:
    con.ping(True)
    cursor = con.cursor()
    cursor.execute('SET autocommit = 0');
    con.commit()
    cursor.executemany("""INSERT IGNORE INTO carpool_data_canada(source,destination,performer,schedule,smoking_status,gender,offer_type) VALUES(%s,%s,%s,%s,%s,%s,%s)""",fullSet)
    con.commit()
    cursor.close()
    return 0
  except Exception as e:
    print("ERROR - Exception inserting car-pool data  - "+str(e))
    logger.error("ERROR - Exception inserting car-pool data  - "+str(e))
    return 1



#Parse all record set inside provided links
def parseAllRecords(soup):
	total_records = soup.find_all('div',class_='panel panel-default')
	for records in total_records:
		tempSet=[]
		body=records.find('div',class_='panel-body')
		footer=records.find('div',class_='panel-footer')
#fetching from and to data
		from_to = body.find('h4')
		if from_to:
			from_to_data = from_to.text.strip()
			from_to_data_new= from_to_data.split('to')
			from_stop = from_to_data_new[0].strip()
			to_stop = from_to_data_new[1].strip()
			# print(from_stop)
			# print(to_stop)
		else:
			from_stop='na'
			to_stop='na'

	#fetching performer data | Driver,Passenger
		performer = body.find('h5')
		if performer:
			performer_type = performer.text.strip()
		else:
			performer_type='na'

	#fetching trip schedule details
		schedule = body.find('div',class_='col-xs-12 col-sm-12 col-md-12 text-center font_15em')
		if schedule:
			schedule_data = schedule.text.strip()
		else:
			schedule_data = 'na'

	#Fetching footer data
		gender='na'
		smoking_habits='na'
		seat_type="na"
		
		if footer:
	#Fetching gender based on span used
			gender = footer.find('span',class_='glyphicons glyphicons-gender-female')
			if gender:
				gender ='Female'
			else:
				gender2 =  footer.find('span',class_='glyphicons glyphicons-gender-male')
				if gender2:
					gender ='Male'
			# print(gender)


	#find smoker & non smokers or na
			smoking = footer.find('img',alt='Non-Smoker')
			if smoking:
				smoking_habits='Non-Smoker'
			else:
				smoking = footer.find('img',alt='Smoker')
				if smoking:
					smoking_habits='Smoker'
			# print(smoking_habits)

	#Fetching seat type value | required/offered
			seat = footer.find_all('strong')
			for test in seat:
				seat_type=seat_type+" "+test.text
			# print(seat_type.strip())

#Insert all data into given list
			tempSet.append(from_stop)
			tempSet.append(to_stop)
			tempSet.append(performer_type)
			tempSet.append(schedule_data)
			tempSet.append(gender)
			tempSet.append(smoking_habits)
			tempSet.append(seat_type)
			fullSet.append(tempSet)


#
# Main function
#
if __name__ == "__main__":
	print("Scraper started!!")
	start_time = time.time()
  
# Update page count range here -> (1 to n-1)
	for page_count in range (1,15):

		new_url=url+str(page_count)

		response = requests.get(new_url,headers={"user-agent":random.choice(uaList)})
		soup = BeautifulSoup(''.join(response.content),'html.parser')

# All carpool links in given page
		links = soup.find_all('span',class_="cell_grp")

		for link in links:
			link_url = link.find('a').get('href')

# Send request to provided page with random User Agent
			resp = requests.get(link_url,headers={"user-agent":random.choice(uaList)})
			soup2 = BeautifulSoup(''.join(resp.content),'html.parser')

#Parse all records in given soup element and move to FullSet
			parseAllRecords(soup2)
			print("Success parsing - "+str(link.find('a').text))

		print("\n All records parsed! Moving to next page - "+str(page_count))
	
	logger.info("JOB FINISHED | records scraped - "+str(len(fullSet)))
	print("JOB FINISHED | records scraped - "+str(len(fullSet)))
	if (insertBulkData()==0):
		print("Success inserting data into carpool_data_canada TABLE!!")
	else:
		print("Error inserting data into MySQLdb")
	tot_time = time.time() - start_time;
	print("Scraping JOB finished in  - %s seconds "%(tot_time))
	logger.info("Scraping JOB finished in -  %s seconds "%(tot_time))
