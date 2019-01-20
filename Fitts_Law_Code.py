import turtle
import random
import win32api, win32con
import time
import math
import os.path
import csv

##
# A simple interface to test Fitts' Law. This simplified experiment, 
# measure users’ abilities to point and click on random circles shown 
# on the screen for different value of the index of difficulty (ID) 
# while using a Mouse or a Trackpad.
#
# Output is a rawData.csv for each run and is stored on the users desktop
# ONLY WORKS with windows computers
#
# By: Levi VonBank and Shrestha Shanker
# 


# Stores all unfinished 120 test cases
circleTestBlocks = []

# Stores points in accordance with cursor location to calculate distance
distPoints = []

# Keeps track of what circles have been used in what order
circleStack = []



# This function returns a randomly picked circle out of a set of 12 tests with 10 test blocks (120 tests)
# @return (diameter, distance, direction)
def getCircle(previous=False):
    circle = None
    if len(circleTestBlocks) > 0 and not previous:
        index = random.randint(0, len(circleTestBlocks)-1)
        circleStack.append([circleTestBlocks[index],None,None,None])
        circle = circleTestBlocks.pop(index)
    else:
        circle = circleStack[len(circleStack)-1][0]
    return translateCircle(circle)



# Makes 120 test from 12 base cases repeating each 10 times
def generateTests():
    circleBaseTests = [('small', 'short', 'left'), ('medium', 'short', 'left'), ('large', 'short', 'left'),
                       ('small', 'long', 'left'), ('medium', 'long', 'left'), ('large', 'long', 'left'),
                       ('small', 'short', 'right'), ('medium', 'short', 'right'), ('large', 'short', 'right'),
                       ('small', 'long', 'right'), ('medium', 'long', 'right'), ('large', 'long', 'right')]

    # Creates 10 test blocks for each
    for i in range(len(circleBaseTests)):
        for y in range(10):
            circleTestBlocks.append(circleBaseTests[i])



# Translates a circles dimensions to pixel values
# @parm circleDim a tuple of dimensions values
# @return a tuple in pixel equivalents of circle
def translateCircle(circleDim):
    dimensions = {'small': 12.5, 'medium': 25, 'large': 50, 'short': 100, 'long': 250, 'right': 1, 'left': -1}
    radius = dimensions[circleDim[0]]
    distance = dimensions[circleDim[1]]
    direction = dimensions[circleDim[2]]
    return (radius, distance, direction)



# Sets up screen property
windowScreen = turtle.Screen()
windowScreen.title("Fitts Law Test")
windowScreen.screensize()
windowScreen.setup(width=1.0, height=1.0)

# bindScreen is a tkinter object
bindScreen = windowScreen.getcanvas()

# Sets up Turtles
drawTurtle = turtle.Turtle()
drawTurtle.hideturtle()
drawTurtle.speed(0)

progressTurtle = turtle.Turtle()
progressTurtle.hideturtle()
progressTurtle.penup()
progressTurtle.setpos(0, -250)

writeTurtle = turtle.Turtle()
writeTurtle.hideturtle()
writeTurtle.speed(0)



# This function draw blue circle based on radius
def drawCircle(tur, rad, color):
    tur.color(color, color)
    tur.begin_fill()
    tur.circle(rad)
    tur.end_fill()



# This function draw a rectangle on screen based on given values
def drawRectangle(tur, x, y, width, height):
    tur.up()
    tur.goto(x, y)
    tur.pendown()
    tur.forward(width)
    tur.left(90)
    tur.forward(height)
    tur.left(90)
    tur.forward(width)
    tur.left(90)
    tur.forward(height)
    tur.left(90)
    tur.penup()



# This function draw circle at a distance based on distance list
# @parm tur the turtle that draws
# @parm circlePix a tuple of pixel valuse
def createCircle(tur, circlePix, redo):
    tur.clear()

    if redo:
        color = "Red"
    else:
        color = "Blue"

    tur.penup()
    tur.goto((circlePix[1] * circlePix[2]), -(circlePix[0]))
    tur.pendown()
    drawCircle(tur, circlePix[0], color)



# Global values to identify missed clicks
redo = False
circlePix = None
errors = 0

def loopClick(x, y):
    global redo, circlePix, errors, clickTimer
    stopTimer()
    
    # If a circle has been tried it checks accuracy and stores data
    if circlePix:
        redo = not insideCircle((x, y), circlePix)
        circleStack[len(circleStack)-1][2] = clickTimer
        circleStack[len(circleStack)-1][3] = calcDistance()
    
    # Sets up for next
    resetCursor()
    testsLeft = len(circleTestBlocks)
    if not redo: progressUpdate(testsLeft)
    
    # Get a circle to test using pixel values to draws it
    circlePix = getCircle(redo)
    createCircle(drawTurtle, circlePix, redo)
    
    # Makes a beep if circle was missed
    if redo: 
        win32api.Beep(750, 300)
        errors +=1
    else: 
        circleStack[len(circleStack)-1][1] = errors
        errors = 0
    
    # Controls a recursive function once it finishes all test cases
    if testsLeft > 0 or redo:
        distPoint()
        startTimer()
        windowScreen.onclick(loopClick)
    else:
        simClick()
        windowScreen.onclick(endScreen)



# Simulates a fake click to escape loop
def simClick():
    x,y = win32api.GetCursorPos() 
    win32api.SetCursorPos((x,y)) 
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)



# Gets coordinates of cursor
def pointerCoordinates(event):
    x, y = event.x, event.y
    distPoints.append((x, y))



# Adds cursor coordinates to a list of distPoints
def distPoint():
    distPoints.clear()
    bindScreen.bind('<Motion>', pointerCoordinates)



# Calculates the distance between points
def calcDistance():
    distance = 0
    if len(distPoints) > 1:
        for index in range(len(distPoints) - 1):
            distance += math.hypot((distPoints[index + 1][0] - distPoints[index][0]),
                                   (distPoints[index + 1][1] - distPoints[index][1]))
    distPoints.clear()
    return distance



# Keeps time between clicks
clickTimer = 0

# Records start time
def startTimer():
    global clickTimer
    clickTimer = currentTime()

# Records end time
def stopTimer():
    global clickTimer
    clickTimer = currentTime() - clickTimer

# Returns the current time in milliseconds
def currentTime():
    return int(round(time.time() * 1000))



# Checks to see if circle was hit
# @parm coor is the x, y coordinates clicked
# @parm circlePix the pixel location of the circle center
# @return hit equals true otherwise false
def insideCircle(coor, circlePix):
    return (math.hypot((coor[0] - (circlePix[1] * circlePix[2])), (coor[1] - 0)) <= (float(circlePix[0])))



# Updates feedback to users with tracked progress
def progressUpdate(testsLeft):
    progressTurtle.clear()
    progressTurtle.write("Tests Left: " + str(testsLeft), font=("Arial", 12, "normal"), align="center")



# Resets cursor to the center of the screen
def resetCursor():
    halfScreenWidth = int(round(win32api.GetSystemMetrics(0) / 2))
    halfScreenHight = int(round(win32api.GetSystemMetrics(1) / 2))
    win32api.SetCursorPos((halfScreenWidth, halfScreenHight))



# Clears window at the end and displays a thank you
def endScreen(x, y):
    drawTurtle.clear()
    writeTurtle.write("Thank you", font=("Arial", 30, "normal"), align="center")
    save()



# Makes a consent screen
def consentScreen():
    # Title
    drawTurtle.up()
    drawTurtle.setpos(0, 250)
    drawTurtle.write("Consent", font=("Arial", 30, "bold"), align="center")
    drawTurtle.setpos(0, 0)

    # Body
    drawTurtle.write("You have been chose to participate in a research study at Minnesota State University, Mankato." +
                     "\nThe purpose of this study is to examine users’ abilities to point and click on random circles shown on a screen." +
                     "\nParticipating in this study is voluntary. You can decide to stop at any time. To withdraw from the study," +
                     "\nyou can close the window before finishing. Results of the study will include only people willing to participate." +
                     "\nIf you have any questions, you may ask the Levi or Shankar." +
                     "\n\nThe responses will be anonymous. There are no direct benefits for participation. The study will include at least 15" +
                     "\nother individuals and should take about 30 minutes per person to complete." +
                     "\n\nIf you agree to participate in the study and are at least 18 years of age, click anywhere to begin." +
                     "\n", font=("Arial", 11, "normal"), align="center")

    # Agreement box
    drawRectangle(drawTurtle, -54, -85, 100, 25)
    drawTurtle.setpos(0, -82)
    drawTurtle.write("I Agree", font=("Arial", 10, "bold"), align="center")
    drawTurtle.setpos(0, 0)



# Calculates the index of difficulty
def indexDifficulty(A, W):
    return math.log2(A/W + 1)



# Exports raw data to csv file on desktop
def save():
    csvfile = os.path.expanduser("~/Desktop") + "/Raw_Data.csv"
    
    for index in range(len(circleStack)):
        circleDim = circleStack[index][0]
        circlePix = translateCircle(circleDim)
        # Sets the 'A', 'W', 'ID' for each circle
        circleStack[index].append(circlePix[1])
        circleStack[index].append(circlePix[0]*2)
        circleStack[index].append(indexDifficulty(circlePix[1], circlePix[0]*2))
        # Breaks up circle tuple
        circleStack[index].insert(0,circleDim[0])
        circleStack[index].insert(1,circleDim[1])
        circleStack[index].insert(2,circleDim[2])
        circleStack[index].remove(circleDim)
        
        
    # Adds Header to data
    circleStack.insert(0,['Size','Gap','Side','Error','Time(ms)','Distance','A','W','ID'])
    
    #Exports a list of lists
    with open(csvfile, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(circleStack)



# Starts running the program
generateTests()
consentScreen()
windowScreen.onclick(loopClick)
turtle.done()