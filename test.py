import requests
from bs4 import BeautifulSoup
import pandas  as pd

def url_ok(url): # checks if the page exists     
    # exception block
    try:   
        # pass the url into
        # request.hear
        response = requests.head(url, allow_redirects=False)
         
        # check the status code
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError as e:
        return e

def get_activity_urls(url): # returns a list of [attraction location, attraction time, [activity links]]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    count = 1 # no of pages scraped


    time_check = soup.find('span', class_ = 'pl-2 opening-hours-text')
    if time_check is not None:
        time = time_check = soup.find('span', class_ = 'pl-2 opening-hours-text').text
    else:
        time = 'N/A'
    location_div = soup.find('div', class_ = 'attraction-location p-1 d-flex')
    location = location_div.find('span', class_ = 'pl-2').text

    activity_details = [location,time,[]]

    #code block for first page
    soup = BeautifulSoup(page.content, 'html.parser')
    activity_cards = soup.find_all('div', class_ = 'tracked-elements')
    for activity_card in activity_cards:
        activity_name = activity_card.find('a', class_ = 'text-dark highlight-able card-link').text
        activity_url = activity_card.find('a', class_ = 'text-dark highlight-able card-link').get('href')
        activity_url = 'https://www.viator.com'+activity_url
        if [activity_name,activity_url] not in activity_details[-1]:
            activity_details[-1].append([activity_name,activity_url])
            print(activity_name + ' added to list!')
    count += 1

    #code block for rest of the pages
    while True:
        page = requests.get(url+'/'+str(count))
        soup = BeautifulSoup(page.content, 'html.parser')
        active_button = soup.find('li', class_ = 'page-item active')
        if active_button.find('a').text == '1':
            print(active_button.find('a').text)
            break
        else:
            activity_cards = soup.find_all('div', class_ = 'tracked-elements')
            for activity_card in activity_cards:
                activity_name = activity_card.find('a', class_ = 'text-dark highlight-able card-link').text
                activity_url = activity_card.find('a', class_ = 'text-dark highlight-able card-link').get('href')
                activity_url = 'https://www.viator.com'+activity_url
                if [activity_name,activity_url] not in activity_details[-1]:
                    activity_details[-1].append([activity_name,activity_url])
                    print(activity_name + ' added to list!')
            count += 1
        
    return activity_details

get_activity_urls('https://www.viator.com/en-IN/Thailand-attractions/Grand-Palace/d20-a2605')