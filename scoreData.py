################################################################
# scoreData
# 
# by: Kendra Wong
# andrew ID: kendrawo
################################################################

import requests
from bs4 import BeautifulSoup

# General Structure/Syntax of webscraping: Webscraping Mini-Lecture
# https://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=eea8b9af-15c7-45cb-baf0-acfb001473d6 
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/ 

# Source to find User Agent:
# https://developers.whatismybrowser.com/useragents/parse/?analyse-my-user-agent=yes 

def getWeatherData(city, state, stateAbbrev):
    categories = {'Air Quality', 'Wind', 'Humidity', 'Clouds', 'Visibility'}
    weatherVals = dict()
    weatherUrl = 'https://www.wunderground.com/weather/us/' + stateAbbrev + '/' + city
    airQualityUrl = 'https://www.iqair.com/us/usa/' + state + '/' + city
    header = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
    weather = requests.get(weatherUrl, headers=header)
    airQual = requests.get(airQualityUrl, headers=header)
    weatherContent = BeautifulSoup(weather.content, 'html.parser')
    airQualValues = {'Good', 'Moderate', 'Unhealthy for Sensitive Groups', \
        'Unhealthy', 'Very Unhealthy', 'Hazardous'}
    airQualContent = BeautifulSoup(airQual.content, 'html.parser')
    cloudValues = {'Sunny', 'Partly Cloudy', 'Mostly Cloudy', 'Cloudy'}

    windSpeed = weatherContent.find('header', class_='wind-speed')
    weatherVals['Wind'] = int(windSpeed.string)

    airQuality = airQualContent.find('span', class_="aqi-status__text")
    weatherVals['Air Quality'] = airQuality.string

    visibility = weatherContent.find(string='Visibility')
    visParent = visibility.find_parent('div')
    visParent = visParent.find_parent('div')
    weatherVals['Visibility'] = int(list(visParent.descendants)[9])

    humidity = weatherContent.find(string='Humidity')
    humParent = humidity.find_parent('div')
    humParent = humParent.find_parent('div')
    weatherVals['Humidity'] = int(list(humParent.descendants)[9])

    clouds = weatherContent.find_all('span', class_='wx-value')[-1]
    weatherVals['Clouds'] = clouds.string

    return weatherVals

def calculateWeatherScore(weatherVals):
    scores = dict()
    weight = 0.1
    # Wind
    if weatherVals['Wind'] <= 6:
        scores['windScore'] = 95 * weight
    elif 7 <= weatherVals['Wind'] <= 10:
        scores['windScore'] = 66 * weight
    elif 10 < weatherVals['Wind'] <= 16:
        scores['windScore'] = 33 * weight
    else:
        scores['windScore'] = 0
    
    weight = 0.15
    # Visibility
    if weatherVals['Visibility'] >= 10:
        scores['visibilityScore'] = 95 * weight
    elif 7 <= weatherVals['Visibility'] < 10:
        scores['visibilityScore'] = 66 * weight
    elif 4 <= weatherVals['Visibility'] < 7:
        scores['visibilityScore'] = 33 * weight
    else:
        scores['visibilityScore'] = 0
    
    # Air Quality
    if weatherVals['Air Quality'] == 'Good':
        scores['aqScore'] = 95 * weight
    elif weatherVals['Air Quality'] == 'Moderate':
        scores['aqScore'] = 66 * weight
    elif weatherVals['Air Quality'] == 'Unhealthy for Sensitive Groups':
        scores['aqScore'] = 33 * weight
    else:
        scores['aqScore'] = 0

    weight = 0.2
    # Humidity
    if 20 < weatherVals['Humidity'] <= 40:
        scores['humidityScore'] = 95 * weight
    elif weatherVals['Humidity'] <= 20:
        scores['humidityScore'] = 66 * weight
    elif 40 < weatherVals['Humidity'] <= 60:
        scores['humidityScore'] = 33 * weight
    else:
        scores['humidityScore'] = 0

    weight = 0.35
    # Cloud Cover
    if weatherVals['Clouds'] == 'Partly Cloudy':
        scores['coverScore'] = 95 * weight
    elif weatherVals['Clouds'] == 'Sunny':
        scores['coverScore'] = 66 * weight
    elif weatherVals['Clouds'] == 'Mostly Cloudy':
        scores['cloudScore'] = 33 * weight
    else:
        scores['cloudScore'] = 0
    weightedScore = 0
    for score in scores:
        weightedScore += int(scores[score])
    return weightedScore
