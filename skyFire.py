################################################################
# SkyFire
# 
# by: Kendra Wong
# andrew ID: kendrawo
################################################################

# import modules
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from geopy.geocoders import Nominatim
from PIL import Image
from cmu_112_graphics import *
import time, os, math
import cityFinder, scoreData

# Sources:
# Basic PIL information:
# https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
# https://pillow.readthedocs.io/en/stable/reference/Image.html 

# Selenium Sources:
# https://selenium-python.readthedocs.io
# https://intoli.com/blog/running-selenium-with-headless-chrome/ 
# https://github.com/cobrateam/splinter/issues/342
# https://www.geeksforgeeks.org/action-chains-in-selenium-python/
# https://stackoverflow.com/questions/27948420/click-at-at-an-arbitrary-position-in-web-browser-with-selenium-2-python-binding
# https://seleniumwithjavapython.wordpress.com/selenium-with-python/advanced-topics/cropping-an-image-using-pil/


def appStarted(app):
    # for webdriver settings
    opts = webdriver.ChromeOptions()
    opts.add_argument('headless')
    opts.add_argument('window-size=2000x1000')
    header = 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
    opts.add_argument(header)
    app.browser = webdriver.Chrome(options=opts)
    app.weatherScore = None

    # initialize location and file variables
    app.zipcode = None
    app.city, app.state, app.stateAbbrev = None, None, None
    app.fileName = None
    app.path = None

    # initialize image, coordinate, and canvas variables
    app.size = None
    app.center = ''
    app.centerX, app.centerY = None, None
    app.clickX, app.clickY = None, None
    app.latConversion = 364000 # 1 degree of latitude is 364,000 feet
    app.longConversion = 288200 # 1 degree of longitude is 288,200 feet

    # initialize booleans
    app.clickedWater = False
    app.inputted = False
    app.inputCanceled = False
    app.instructionsPopUp = False

    # initialize title animation variables
    app.xy1 = []
    app.xy2 = []
    app.xy3 = []
    app.xy4 = []
    app.xy5 = []
    getSineCoords(app)
    app.cx = app.height//8
    app.cy = app.height*3//4
    app.r = 30
    app.mapDrawn = False
    app.red = 22
    app.green = 73
    app.blue = 138
    app.skyColor = rgbString(app.red, app.green, app.blue)
    app.dr, app.dg, app.db = 0, 0, 0

    resetVariables(app)

def resetVariables(app):
    # reinitialize elevation grid variables
    app.coordsList = []
    app.elevationDict = dict()
    app.elevationCanvasCoords = dict()
    app.bestElevationCoords = None
    app.clickedElevationSet = set()
    app.highest = 0
    
def keyPressed(app, event):
    if event.key == 'r':
        appStarted(app)
    if event.key == 's': # search for another zipcode
        resetVariables(app)
        inputZipcode(app, 'Enter US zipcode here: ')
    if event.key == 'c':
        app.clickedElevationSet = set()
    if event.key == 'i' and app.inputted == True:
        app.instructionsPopUp = not app.instructionsPopUp

def mousePressed(app, event):
    if app.inputted == False:
        return
    if app.inputCanceled == False:
        app.clickX, app.clickY = event.x, event.y
        pixelColor = getImagePixel(app)
        rVal = pixelColor[0]
        gVal = pixelColor[1]
        bVal = pixelColor[2]
        if pixelColor == (151, 179, 227) or pixelColor == (110, 148, 211) or\
            pixelColor == (162, 192, 244):
            app.clickedWater = True
        else:
            app.clickedWater = False
            newCoordOpt(app)

def getImagePixel(app):
    pixelX = (app.clickX - ((app.width - app.size[0])//2)) / app.scaleFactor
    pixelY = app.clickY / app.scaleFactor
    imageRGB = app.image.convert('RGB')
    pixelRGB = imageRGB.getpixel((pixelX, pixelY))
    return pixelRGB

def inputZipcode(app, message):
    app.inputted = True
    app.zipcode = app.getUserInput(message)
    try:
        getLocationData(app)
    except:
        inputZipcode(app, 'Try again. Make sure zipcode is in the US: ')
        app.mapLoading = False

def getLocationData(app):
    if app.zipcode == None:
        app.inputCanceled = True
    else:
        app.mapLoading = True
        app.city, app.state, app.stateAbbrev = cityFinder.findCity(app.zipcode)
        app.fileName = app.zipcode + '.png'
        app.path = '/Users/kendra/Desktop/15112/term project'
        getCoordsAndScale(app, app.zipcode)
        loadScreenshot(app, app.zipcode)
        weatherVals = scoreData.getWeatherData(app.city, app.state, app.stateAbbrev)
        app.weatherScore = scoreData.calculateWeatherScore(weatherVals)
        getCoordsList(app)
        getElevationGrid(app)
        getElevationCanvasCoords(app)
        app.mapDrawn = True

def newCoordOpt(app):
    # get new coordinates from mouse press and optimize score
    newLat, newLong, newCoords = getClickedCoords(app)
    zipcode = cityFinder.findZipcode(newLat, newLong)
    try:
        if '-' in zipcode:
            zipcode = zipcode.split('-')[0]
        if zipcode != app.zipcode:
            app.city, app.state, app.stateAbbrev = cityFinder.findCity(zipcode)
            weatherVals = scoreData.getWeatherData(app.city, app.state, app.stateAbbrev)
            app.weatherScore = scoreData.calculateWeatherScore(weatherVals)
    except:
        app.city, app.state, app.stateAbbrev = cityFinder.findLocation(newLat, newLong)

    clickedElevation = getElevation(app, newCoords)
    if clickedElevation > app.highest:
        app.highest = clickedElevation
        app.bestElevationCoords = (app.clickX, app.clickY)
    coordsAndElevation = (app.clickX, app.clickY, clickedElevation)
    app.clickedElevationSet.add(coordsAndElevation)

def timerFired(app):
    if app.mapDrawn == True:
        app.scaleFactor = min(app.width/app.image.size[0], app.height/app.image.size[1])
        app.scaledMap = app.scaleImage(app.image, app.scaleFactor)
    if app.inputted == False:
        app.cx += 5
        colorFade(app)
        app.red += 5*app.dr
        app.green += 5*app.dg
        app.blue += 5*app.db
        app.skyColor = rgbString(int(app.red), int(app.green), int(app.blue))
        if '-' in app.skyColor:
            app.skyColor = app.skyColor.replace('-', '0')
        x = (app.cx - app.width//2)
        app.cy = parabola(app, x)
        if app.cy >= (app.height*3//4 + app.r):
            app.cx = app.width//8
            app.red, app.green, app.blue = 22, 73, 138
            app.dr, app.dg, app.db = 0, 0, 0

# color RGB values: https://www.schemecolor.com/ 
# color fading: https://code.activestate.com/recipes/580761-tkinter-frame-with-gradient/ 
def colorFade(app):
    increment = (app.width - app.width//4)//10
    if app.width//8 < app.cx <= 288:
        app.skyColor = rgbString(22, 73, 138)
    elif 288 < app.cx <= 396:
        app.dr = (89-22)/increment
        app.dg = (149-73)/increment
        app.db = (183-138)/increment
    elif 396 < app.cx <= 504:
        app.dr = (181-89)/increment
        app.dg = (214-149)/increment
        app.db = (224-183)/increment
    elif 504 < app.cx <= 612:
        app.dr = (199-181)/increment
        app.dg = (225-214)/increment
        app.db = (229-224)/increment
    elif 612 < app.cx <= 720:
        app.dr = (250-199)/increment
        app.dg = (251-225)/increment
        app.db = (189-229)/increment
    elif 720 < app.cx <= 828:
        app.dr = (253-250)/increment
        app.dg = (224-251)/increment
        app.db = (80-189)/increment
    elif 936 < app.cx <= 1044:
        app.dr = (241-253)/increment
        app.dg = (179-224)/increment
        app.db = (81-80)/increment
    elif 1044 < app.cx <= 1152:
        app.dr = (254-241)/increment
        app.dg = (135-179)/increment
        app.db = (20-81)/increment
    elif 1152 < app.cx <= 1260:
        app.dr = (253 - 254)/increment
        app.dg = (94-135)/increment
        app.db = (83-20)/increment
    elif app.cx > 1260:
        app.dr = (227-253)/increment
        app.dg = (66-94)/increment
        app.db = (52-83)/increment
        
# from: https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    if r > 255:
        r = 255
    elif r < 0:
        r = 0
    if g > 255:
        g = 255
    elif g < 0:
        g = 0
    if b > 255:
        b = 255
    elif b < 0:
        b = 0
    return f'#{r:02x}{g:02x}{b:02x}'

def loadScreenshot(app, zipcode):
    app.image = app.loadImage(app.fileName)
    app.scaleFactor = min(app.width/app.image.size[0], app.height/app.image.size[1])
    app.scaledMap = app.scaleImage(app.image, app.scaleFactor)
    app.size = app.scaledMap.size

def cropImage(app):
    # crop the image to only show the map and replace the full screen image
    image = Image.open(app.fileName)
    left = 900
    top = 300
    right = left + 2000
    bottom = top + 1400
    image = image.crop((left, top, right, bottom))
    image.save(app.fileName)

def getCoordsAndScale(app, zipcode):
    # copy center coordinates to clipboard
    url = 'https://www.google.com/maps/search/' + zipcode + '/data=!5m1!1e4'
    app.browser.get(url)
    # wait until webpage is loaded
    element = WebDriverWait(app.browser, 10).until(
        EC.presence_of_element_located((By.ID, 'widget-scale-label')))
    # if the screenshot is not already in files, take a full page screenshot
    if app.fileName not in os.listdir(app.path):
        app.browser.save_screenshot(app.fileName)
        cropImage(app)
    # web scrape the scale of Google Maps and the number of pixels per scale value
    scale = app.browser.find_element(By.ID, 'widget-scale-label').text
    if 'mi' in scale:
        app.mapScale = int(scale.replace(' mi', '')) * 5280
    else:
        app.mapScale = int(scale.replace(' ft', ''))
    pixels = app.browser.find_element(By.CLASS_NAME,\
        'mapsTactileClientScale__widget-scale-ruler').get_attribute('outerHTML')
    app.pixels = int(pixels.split()[-1].replace('style="width:', '').replace('px"></div>', ''))
    anchorPt = app.browser.find_element(By.ID, 'searchbox_form')
    # move to an anchor point and automate a mouse press to get center coordinates
    action = ActionChains(app.browser)
    action.move_to_element_with_offset(anchorPt, 880, 480).context_click().perform()
    element = WebDriverWait(app.browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, \
        'mapsTactileClientActionmenu__action-menu-entry-text')))
    app.centerCoords = app.browser.find_element(By.CLASS_NAME, \
        'mapsTactileClientActionmenu__action-menu-entry-text').text
    app.centerX = float(app.centerCoords.split(',')[0])
    app.centerY = float(app.centerCoords.split(',')[1])

def canvasToCoords(app, x, y):
    # convert canvas coordinates to latitude and longitude
    dx = app.height//2 - y
    dy = x - app.width//2
    lat = app.centerX + (1/(app.latConversion/app.mapScale))/(app.pixels*2) * dx / app.scaleFactor
    lon = app.centerY + (1/(app.longConversion/app.mapScale))/(app.pixels*2) * dy / app.scaleFactor
    return lat, lon

def coordsToCanvas(app, lat, lon):
    # convert latitude and longitude to canvas coordinates
    dx = float(lon) - float(app.centerCoords.split(', ')[1])
    dy = float(lat) - float(app.centerCoords.split(', ')[0])
    canvasX = int((app.width//2 + (app.latConversion/app.mapScale)*(app.pixels/2) * dx / app.scaleFactor)//1)
    canvasY = int((app.height//2 - (app.longConversion/app.mapScale)*(app.pixels/2) * dy / app.scaleFactor)//1)
    return canvasX, canvasY

def getCoordsList(app):
    # use a small increment to get a list of coordinates that will be used 
    #    the elevation grid
    for i in range(3):
        for j in range(3):
            coordStr1 = str(app.centerX + 0.008*i) + ', ' + str(app.centerY + 0.008*j)            
            coordStr2 = str(app.centerX - 0.008*i) + ', ' + str(app.centerY + 0.008*j)
            coordStr3 = str(app.centerX + 0.008*i) + ', ' + str(app.centerY - 0.008*j)
            coordStr4 = str(app.centerX - 0.008*i) + ', ' + str(app.centerY - 0.008*j)
            app.coordsList.append(coordStr1)
            app.coordsList.append(coordStr2)
            app.coordsList.append(coordStr3)
            app.coordsList.append(coordStr4)

def getClickedCoords(app):
    newLat, newLong = canvasToCoords(app, app.clickX, app.clickY)
    newCoordString = str(newLat) + ', ' + str(newLong)
    return newLat, newLong, newCoordString

def getElevation(app, coordinates):
    # use selenium to web scrape elevation values given latitude and longitude
    url = 'https://www.freemaptools.com/elevation-finder.htm'
    app.browser.get(url)
    searchBox = app.browser.find_element(By.ID, 'locationSearchTextBox')
    searchBox.send_keys(coordinates)
    searchBox.send_keys(Keys.RETURN)
    time.sleep(2)
    elevation = app.browser.find_element(By.XPATH, '//div[@id="content"]/div[4]').text
    elevation = float(elevation.splitlines()[0].split()[3])
    return elevation    

def getElevationGrid(app):
    # get elevation for each coordinate pair in the list of coordinates
    #   to create a grid of elevation values
    url = 'https://www.freemaptools.com/elevation-finder.htm'
    app.browser.get(url)
    searchBox = app.browser.find_element(By.ID, 'locationSearchTextBox')
    for coordinates in app.coordsList:
        searchBox.clear()
        searchBox.send_keys(coordinates)
        searchBox.send_keys(Keys.RETURN)
        time.sleep(3)
        elevation = app.browser.find_element(By.XPATH, '//div[@id="content"]/div[4]').text
        # if the page doesn't load in time, try again
        try:
            elevation = float(elevation.splitlines()[0].split()[3])
            app.elevationDict[coordinates] = elevation
        except:
            time.sleep(1)
            elevation = app.browser.find_element(By.XPATH, '//div[@id="content"]/div[4]').text
            elevation = float(elevation.splitlines()[0].split()[3])
            app.elevationDict[coordinates] = elevation

def getElevationCanvasCoords(app):
    # to figure out where to print the elevation values on the canvas, 
    #   convert all coordinates to canvas coordinates
    for coords in app.elevationDict:
        lat = float(coords.split(', ')[0])
        lon = float(coords.split(', ')[1])
        x, y = coordsToCanvas(app, lat, lon)
        app.elevationCanvasCoords[(x, y)] = app.elevationDict[coords]
    for coords in app.elevationCanvasCoords:
        if app.elevationCanvasCoords[coords] > app.highest:
            app.highest = app.elevationCanvasCoords[coords]
            app.bestElevationCoords = coords

def getSineCoords(app):
    # use a sine function to create the waves on the title page
    for x in range(app.width):
        # x coordinates
        app.xy1.append(x*1)
        app.xy2.append(x*2)
        app.xy3.append(x*3)
        app.xy4.append(x*2)
        app.xy5.append(x*2)
        # y coordinates
        app.xy1.append(int(math.sin(x * 0.04) * 5) + app.height*3//4)
        app.xy2.append(int(math.sin(x * 0.06) * 8) + app.height*7//8)
        app.xy3.append(int(math.sin(x * 0.1) * 7) + app.height*31//32)
        app.xy4.append(int(math.sin(x * 0.05) * 6) + app.height*13//16)
        app.xy5.append(int(math.sin(x * 0.08) * 6) + app.height*29//32)

def parabola(app, x):
    # this is the path the sun follows on the title page
    y = (1/1000) * x**2 + app.height//3
    return y

def drawTitleAnimation(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=app.skyColor, width=0)
    canvas.create_oval(app.cx-app.r, app.cy-app.r, app.cx+app.r, app.cy+app.r, \
        fill='#EF5200', width=0)
    canvas.create_line(app.xy1, fill='#006994', width=20)
    canvas.create_rectangle(0, app.height*3//4, app.width, app.height, \
        fill='#006994', width=0)
    canvas.create_line(app.xy2, fill='#050A30')
    canvas.create_line(app.xy3, fill='#050A30')
    canvas.create_line(app.xy4, fill='#050A30')
    canvas.create_line(app.xy5, fill='#050A30')

def drawMap(app, canvas):
    canvas.create_image(app.width//2, app.height//2, \
        image=ImageTk.PhotoImage(app.scaledMap))

def drawInstructions(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height//12, fill='#fff7eb', width=0)
    city = app.city.replace('-', ' ')
    canvas.create_text(app.width/2, app.height//30, \
        text=f'there is a {app.weatherScore}% chance of a colorful sky in {city}',
        font='georgia 15')
    canvas.create_text(app.width//2, app.height//15, \
        text='click on the map find the best spot to watch the sky!', \
        font='georgia 12 bold')
    canvas.create_text(100, 50, text='press i to see instructions', \
        font='georgia 12 bold')

def drawElevation(app, canvas):
    if app.bestElevationCoords != None:
        x = app.bestElevationCoords[0]
        y = app.bestElevationCoords[1]
        canvas.create_rectangle(x-25, y-10, x+25, y+10, fill='yellow')
    for coords in app.elevationCanvasCoords:
        x = coords[0]
        y = coords[1]
        elevation = str(app.elevationCanvasCoords[coords])
        canvas.create_text(x, y, text=elevation, font='georgia 12 bold')
    for i in app.clickedElevationSet:
        canvas.create_text(i[0], i[1], text=i[2], font='georgia 12 bold')

def drawWaterMessage(app, canvas):
    canvas.create_rectangle(app.width//2 - 240, app.height*15//16 - 10,\
        app.width//2 + 240, app.height*15//16 + 10, fill='yellow', width=0)
    canvas.create_text(app.width//2, app.height*15//16,\
        text='you clicked on water! click on land to get better elevation.',\
            font='georgia 15 bold')

def drawTitle(app, canvas):
    canvas.create_text(app.width//2, app.height//4, text='SkyFire', \
        font='georgia 50 bold')
    canvas.create_text(app.width//2, app.height//4 + 50, text='a sunrise/sunset predictor', \
        font='georgia 25')
    
def drawTitleInstructions(app, canvas):
    canvas.create_text(app.width//2, app.height//2, text='Instructions:',\
        font='georgia 25 bold')
    instructions = [
        'Press s to search for a zipcode',
        'Once you input a zipcode, the app will take about 2 minutes to load',
        'A map will pop up with a grid of elevation values',
        'You can click on the map to find more specific elevations for different points',
        'These elevation values (in feet) will print on the map wherever you clicked',
        'If the map gets too cluttered with elevation values, press c to clear the additional elevations',
        'Press r to go back to the title screen',
        'Press s again to search for another zipcode',
        'Enjoy!'
    ]
    messageHeight = app.height//2 + 30
    for line in instructions:
        canvas.create_text(app.width/2, messageHeight, text=line,\
            font='georgia 20')
        messageHeight += 30

def drawPopUpInstructions(app, canvas):
    canvas.create_rectangle(0, 0, app.width*3//10, app.height//2, fill='#fff7eb', width=0)
    canvas.create_text(100, 50, text='press i to hide instructions', \
        font='georgia 12 bold')
    canvas.create_text(app.width//7, app.height//8, text='Instructions:',\
        font='georgia 20 bold')
    instructions = [
        'Press s to search for another zipcode',
        'Once you input a zipcode,',
        'the app will take about 2 minutes to load',
        'A new map will pop up with a grid of elevation values',
        'You can click on the map to find',
        'more specific elevations for different points',
        'These elevation values (in feet)',
        'will print on the map wherever you clicked',
        'If the map gets too cluttered with elevation values,', 
        'press c to clear the additional elevations',
    ]
    messageHeight = app.height//8 + 20
    for line in instructions:
        canvas.create_text(app.width//7, messageHeight, text=line,\
            font='georgia 15')
        messageHeight += 20

def redrawAll(app, canvas):
    if app.mapDrawn == False:
        drawTitleAnimation(app, canvas)
        drawTitle(app, canvas)
        drawTitleInstructions(app, canvas)
    if app.mapDrawn == True:
        drawMap(app, canvas)
        drawElevation(app, canvas)
        if app.weatherScore != None:
            drawInstructions(app, canvas)
    if app.clickedWater == True:
        drawWaterMessage(app, canvas)
    if app.instructionsPopUp == True:
        drawPopUpInstructions(app, canvas)

def runSkyFire():
    runApp(width=1440, height=795)

def main():
    runSkyFire()

if __name__ == '__main__':
    main()


