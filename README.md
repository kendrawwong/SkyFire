# SkyFire
Description:
This app is called the SkyFire. It takes a US zipcode imputed by the app user and finds the corresponding city and state. This information is then used to web scrape weather data from wunderground.com as well as take a screenshot of Google Maps of where the zipcode boundaries are. A “good” sunrise or sunset - vibrant colors across the entire sky - is determined by cloud cover, humidity, visibility, wind, and air quality. All of these values are weighted differently to determine a percentage score of the chance of a “good” sunset. The Google Maps image is uploaded into the app so the user can click on a point within the map, which will return latitude and longitude coordinates. A grid of elevation values will also be displayed across the map. These coordinates will then be used to web scrape elevation data, which will be displayed on the map. The highest elevation value will be highlighted, suggesting a location to go watch the sunrise/sunset.

How to run the project:
Open and run the skyFire.py file, which will open the app.

Libraries:
Requests, bs4 (Beautiful Soup), Selenium, geopy, and PIL must be installed.
This app uses cmu_112_graphics.py

Demo Video:
https://youtu.be/lz07259j-wU
