# Boston scrape
import requests
from pyquery import PyQuery
import time
import traceback

TEXAS_STATE_ID = 55
LA_STATE_ID = 26
STATE_ID = LA_STATE_ID

def request_data(city, age, stateID):
    url = "http://registration.baa.org/2014/cf/public/iframe_EntryLists.cfm?mode=results"
    returnData = {}

    requestData = {
        "City": city,
        "StateID":stateID,
        "AgeLowID": age
    }

    defaultData = {
        "VarBibNumber":"",
        "VarLastName":"",
        "VarFirstName":"",
        "VarZipList":"",
        "VarCountryOfResList":0,
        "VarCountryOfCtzList":0,
        "GenderID":0
    }
    
    data = dict(requestData.items() + defaultData.items())

    success = False
    while not success:
        try:
            r = requests.post(url=url, data=data, timeout=3)
            success = True
        except Exception, e:
            print("Exception occurred: Sleeping for 3 seconds")
            print(traceback.format_exc())
            time.sleep(3)

    time.sleep(.1)
    return r.content

def extract_data(resultHTML):
    jQuery = PyQuery(resultHTML)

    # The main results table
    peopleTable = jQuery("table.tablegrid_table")

    # Skip the first element, which are table headers
    peopleRows = jQuery(peopleTable).find("tr")[1:]

    peopleList = []

    for row in peopleRows:
        tds = jQuery(row).children()
        if len(tds) > 5:
            person = {
                "name": jQuery(tds[2]).text(),
                "age": jQuery(tds[3]).text(),
                "city": jQuery(tds[5]).text()
            }
            peopleList.append(person)
            
    return peopleList

def output_data(peopleList):
    with open("la-data.txt", "a") as f:
        for p in peopleList:
            f.write("%s;%s;%s\n" % (p['city'].encode('utf8'), p['name'].encode('utf8'), p['age']))

####################
# Begin execution
####################

if __name__ == "__main__":
    with open("la-cities.txt") as f:
        cities = [x.strip() for x in f.readlines()]

    for city in cities:
        print("Scraping %s..." % city)

        html = request_data(city, 0, STATE_ID)
        peopleList = extract_data(html)

        if len(peopleList) >= 50:
            print("\t50 entrants found, scraping by age")
            for age in xrange(18, 100+1):
                print("\tGetting age %d" % age)
                html = request_data(city, age, STATE_ID)
                peopleList = extract_data(html)
                print("\t\t %d found" % len(peopleList))
                output_data(peopleList)
        else:
            print("\tOnly %d entrants found, exporting" % len(peopleList))
            output_data(peopleList)
