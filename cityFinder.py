################################################################
# cityFinder
# 
# by: Kendra Wong
# andrew ID: kendrawo
################################################################

from geopy.geocoders import Nominatim

# How to get address details from a zipcode using geopy (and vice versa)
# https://geopy.readthedocs.io/en/stable/ 
def findCity(zipcode):

    states = {'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', \
              'arkansas': 'ar', 'california': 'ca', 'colorado': 'co', \
              'connecticut': 'ct', 'delaware': 'de', 'florida': 'fl', \
              'georgia': 'ga', 'hawaii': 'hi', 'idaho': 'id', 'illinois': 'il',\
              'indiana': 'in', 'iowa': 'ia', 'kansas': 'ks', 'kentucky': 'ky', \
              'louisiana': 'la', 'maine': 'me', 'maryland': 'md', \
              'massachussetts': 'ma', 'michigan': 'mi', 'minnesota': 'mn', \
              'mississippi': 'ms', 'missouri': 'mo', 'montana': 'mt', \
              'nebraska': 'ne', 'nevada': 'nv', 'new hampshire': 'nh', \
              'new jersey': 'nj', 'new mexico': 'nm', 'new york': 'ny', \
              'north carolina': 'nc', 'north dakota': 'nd', 'ohio': 'oh', \
              'oklahoma': 'ok', 'oregon': 'or', 'pennsylvania': 'pa', \
              'rhode island': 'ri', 'south carolina': 'sc', \
              'south dakota': 'sd', 'tennessee': 'tn', 'texas': 'tx', \
              'utah': 'ut', 'vermont': 'vt', 'virginia': 'va', \
              'washington': 'wa', 'west virginia': 'wv', 'wisconsin': 'wi', \
              'wyoming': 'wy'}

    geolocator = Nominatim(user_agent="cityFinder")
    location = geolocator.geocode(query={'postalcode':zipcode}, country_codes='US')
    if location != None:
        address = list(location.address.split(', '))
        for i in range(1,(len(address) - 2)):
            if address[1].lower() not in states:
                address.pop(1)
        city = address[0].replace(' ','-').lower()
        if 'township' in city:
            city = city.replace('-township', '')
        state = address[1].lower()
        stateAbbrev = states[state]
        state = state.replace(' ', '-')
        return (city, state, stateAbbrev)
    return None

def findZipcode(lat, lon):
    geolocator = Nominatim(user_agent="zipcodeFinder")
    coordStr = str(lat) + ', ' + str(lon)
    location = geolocator.reverse(coordStr)
    try:
        zipcode = (location.raw['address']['postcode'])
        return zipcode
    except:
        return None

def findLocation(lat, lon):

    states = {'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', \
            'arkansas': 'ar', 'california': 'ca', 'colorado': 'co', \
            'connecticut': 'ct', 'delaware': 'de', 'florida': 'fl', \
            'georgia': 'ga', 'hawaii': 'hi', 'idaho': 'id', 'illinois': 'il',\
            'indiana': 'in', 'iowa': 'ia', 'kansas': 'ks', 'kentucky': 'ky', \
            'louisiana': 'la', 'maine': 'me', 'maryland': 'md', \
            'massachussetts': 'ma', 'michigan': 'mi', 'minnesota': 'mn', \
            'mississippi': 'ms', 'missouri': 'mo', 'montana': 'mt', \
            'nebraska': 'ne', 'nevada': 'nv', 'new hampshire': 'nh', \
            'new jersey': 'nj', 'new mexico': 'nm', 'new york': 'ny', \
            'north carolina': 'nc', 'north dakota': 'nd', 'ohio': 'oh', \
            'oklahoma': 'ok', 'oregon': 'or', 'pennsylvania': 'pa', \
            'rhode island': 'ri', 'south carolina': 'sc', \
            'south dakota': 'sd', 'tennessee': 'tn', 'texas': 'tx', \
            'utah': 'ut', 'vermont': 'vt', 'virginia': 'va', \
            'washington': 'wa', 'west virginia': 'wv', 'wisconsin': 'wi', \
            'wyoming': 'wy'}

    geolocator = Nominatim(user_agent="locationFinder")
    coordStr = str(lat) + ', ' + str(lon)
    location = geolocator.reverse(coordStr)
    city = location.raw['address']['city'].replace(' ', '-').lower()
    if 'township' in city:
        city = city.replace('-township', '')
    state = location.raw['address']['state'].lower()
    stateAbbrev = states[state]
    state = state.replace(' ', '-')
    return (city, state, stateAbbrev)
