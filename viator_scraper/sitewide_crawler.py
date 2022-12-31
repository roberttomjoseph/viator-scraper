"""This module contains the code for crawling all the city links for a specified
country and then crawling all the attraction links for each city. It then crawls
the activity links for every attraction and returns a dictionary with some information
about the attraction and the activities."""

import json
import requests
from bs4 import BeautifulSoup


def url_ok(url):
    """This function checks if the page exists."""
    try:
        response = requests.head(url, allow_redirects=False, timeout=5)
        return response.status_code == 200
    except requests.ConnectionError as exception:
        return exception

def get_attraction_links(url,stop):
    """returns a dictionary of country: [attraction name, attraction link, []]"""
    activity_list = requests.get(url, timeout=5)
    soup = BeautifulSoup(activity_list.content, 'html.parser')
    country_name = soup.find('span', class_ = 'font-weight-bold mb-0 geo__hub__title').text
    activity_urls = {country_name:[]}
    count = 1 #count of the page number it's currently scraping
    #below is the code block for scraping the first page
    activity_cards = soup.find_all('div', class_ ="mb-lg-4 mb-3 col-lg-4 col-md-12 pl-lg-3 pr-lg-2")
    for activity_card in activity_cards:
        activity_url = activity_card.find('a', class_ = "text-dark link-unstyled").get('href')
        activity_url = 'https://www.viator.com'+activity_url
        activity_name = activity_card.find('h3').text
        activity_urls[country_name].append([activity_name,activity_url,[]])
        print('Link for', activity_name, 'ATTRACTION added to list!')
    count += 1


    #below is the code block for scraping the rest of the pages
    url = url+'/'+str(count)
    while url_ok(url) and count < stop:
        url = url[:-1] + str(count)
        activity_list = requests.get(url, timeout=5)
        soup = BeautifulSoup(activity_list.content, 'html.parser')
        activity_cards = soup.find_all('div', class_ ="mb-0 mb-md-3")
        for activity_card in activity_cards:
            activity_url = activity_card.find('a', class_ = "text-dark").get('href')
            activity_url = 'https://www.viator.com'+activity_url
            activity_name = activity_card.find('a', class_ = 'text-dark').text
            activity_urls[country_name].append([activity_name,activity_url,[]])
            print('Link for', activity_name, 'ATTRACTION added to list!')
        count += 1

    return activity_urls

def get_activity_urls(url,stop):
    """returns a list of [attraction location, attraction time, [activity links,[]]]"""
    page = requests.get(url, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')

    count = 1 # no of pages scraped


    time_check = soup.find('span', class_ = 'pl-2 opening-hours-text')
    if time_check is not None:
        time = time_check = soup.find('span', class_ = 'pl-2 opening-hours-text').text
    else:
        time = 'N/A'
    location_div = soup.find('div', class_ = 'attraction-location p-1 d-flex')
    if location_div is not None:
        location = location_div.find('span', class_ = 'pl-2').text
    else:
        location = 'N/A'

    activity_details = [location,time,[]]

    #code block for first page
    soup = BeautifulSoup(page.content, 'html.parser')
    activity_cards = soup.find_all('div', class_ = 'tracked-elements')
    for activity_card in activity_cards:
        activity_name = activity_card.find(
            'a',
            class_ = 'text-dark highlight-able card-link'
            ).text
        activity_url = activity_card.find(
            'a',
            class_ = 'text-dark highlight-able card-link'
            ).get('href')
        activity_url = 'https://www.viator.com'+activity_url
        if [activity_name,activity_url,[]] not in activity_details[2]:
            activity_details[-1].append([activity_name,activity_url,[]])
            print(activity_name + ' ACTIVITY added to list!')
    count += 1
    #code block for rest of the pages
    while count < stop:
        page = requests.get(
            url+'/'+str(count),
            timeout=5
            )
        soup = BeautifulSoup(page.content, 'html.parser')
        active_button = soup.find('li', class_ = 'page-item active')
        if active_button.find('a').text == '1':
            break
        activity_cards = soup.find_all('div', class_ = 'tracked-elements')
        for activity_card in activity_cards:

            activity_name = activity_card.find(
                'a',
                class_ = 'text-dark highlight-able card-link'
                ).text

            activity_url = activity_card.find(
                'a',
                class_ = 'text-dark highlight-able card-link'
                ).get('href')
            activity_url = 'https://www.viator.com'+activity_url

            if [activity_name,activity_url,[]] not in activity_details[2]:
                activity_details[-1].append([activity_name,activity_url,[]])
                print(activity_name + ' ACTIVITY added to list!')
        count += 1
    return activity_details

def get_data(url):
    """returns a dictionary of activity name:[price, adult_no]"""
    activity_url = url
    activity_ = requests.get(activity_url, timeout=5)
    soup = BeautifulSoup(activity_.content, 'html.parser')

    activity_title_ = soup.title.text

    price = soup.find('span', class_ = 'moneyView__2HPx defaultColor__1NL9').text

    adult_div = soup.find('div', class_ = "input__32lw")
    adult_no = adult_div.find('input', class_ = "input__2pmO md__2bZz").get('value')

    activity_data_ = [price, adult_no]

    print(activity_title_ +' ACTIVITY DATA done!')

    return activity_data_

attractions = get_attraction_links('https://www.viator.com/en-IN/Thailand/d20',1)

with open('json_dumps/attractions.json', 'w', encoding="utf-8") as fp:
    json.dump(attractions, fp, indent = 2)

for ii, attraction in enumerate(attractions['Thailand']):
    activities = get_activity_urls(attraction[1],1)
    attractions['Thailand'][ii][2] = activities

with open('json_dumps/activities_raw.json', 'w', encoding="utf-8") as fp:
    json.dump(attractions, fp, indent = 2)

for attraction in attractions['Thailand']:
    for activity in attraction[2][2]:
        activity_link = activity[1]
        activity_data = get_data(activity_link)
        activity[2] = activity_data
        print(activity)

with open('json_dumps/complete_raw_data.json', 'w', encoding="utf-8") as outfile:
    json.dump(attractions, outfile,indent=2)
