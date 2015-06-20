"""
Make the graphical interface for the restaurant recommendation engine.

We want to have different drop down boxes and a star rating that can be 
associated with each.

The output is the recommedation, and it gives you a map and directions
from your current location to the restaurant.
"""

import sys
sys.path.append('../cluster')
import minwise
import finder # finder finds your location (coordinates)
import pandas as pd # use for data analysis
from Tkinter import *
from PIL import Image, ImageTk # use to plot map image on canvas
import googlemap # call map APIs
import string

class Engine(object):
    # this is the only class. everything's in here
    def __init__(self, root, frame):
        self.initScreen(root, frame)
        self.screenObjects()
        self.graphics(root, frame)
        self.graphics2(root, frame)
        self.canvasObjects()

    def initScreen(self, root, frame):
        # we need canvas and frame ability for this (the drop downs are frame
        # objects in tkinter)
        self.root = root
        self.frame = frame
        self.bg = 'skyblue'
        self.canvas = Canvas(root, width=700, height=500, background=self.bg)
        self.canvas.grid(row=0, column=1)
        self.frame.grid(row=0,column=0, sticky='n')
        self.width = 700
        self.height = 500
        # Frame section
        self.frame = frame
        # define the drop down box selections
        self.stvar = StringVar()
        self.stvar2 = StringVar()
        self.stvar3 = StringVar()
        # set their initial values
        self.stvar.set('')
        self.stvar2.set('')
        self.stvar3.set('')

    def graphics(self, root, frame):
        # draw the frame objects
        # frame objects have a grid system to lay them out
        self.result = []
        self.recommendation = ''
        #self.url = 'restaurant-names.csv'
        self.url = self.data['Name']
        #self.choices = self.flatten(pd.read_csv(self.url).values.tolist())
        self.choices = sorted(self.url.values.tolist())
        # http://stackoverflow.com/questions/21011777/how-can-i-remove-
        # nan-from-list-python-numpy
        self.choices = [x for x in self.choices if str(x) != 'nan']
        self.option = (OptionMenu(self.frame, self.stvar, *self.choices).
                                  grid(row=0, column=1, sticky="ne"))
        Label(self.frame, text="Restaurant:", font='Quicksand').grid(row=0,
              column=0, sticky="nwe")
        self.slider1 = (Scale(self.frame, from_=1, to=5, orient=HORIZONTAL, 
                        command=self.ratings1).grid(row=1, column=1, 
                        sticky="nwe"))

        Label(self.frame, text="Rating:", font='Quicksand').grid(row=1,
              column=0, sticky="nwe")
        self.option = (OptionMenu(self.frame, self.stvar2, *self.choices).
                                  grid(row=2, column=1, sticky="ne"))

    def graphics2(self, root, frame):
        Label(self.frame, text="Restaurant:", font='Quicksand').grid(row=2,
              column=0, sticky="nwe")
        self.slider2 = (Scale(self.frame, from_=1, to=5, orient=HORIZONTAL, 
                        command=self.ratings2).grid(row=3, column=1, 
                        sticky="nwe"))
        Label(self.frame, text="Rating:", font='Quicksand').grid(row=3,
              column=0, sticky="nwe")
        self.option = (OptionMenu(self.frame, self.stvar3, *self.choices).
                                  grid(row=4, column=1, sticky="ne"))
        Label(self.frame, text="Restaurant:", font='Quicksand').grid(row=4,
              column=0, sticky="nwe")
        self.slider3 = (Scale(self.frame, from_=1, to=5, orient=HORIZONTAL,
                        command=self.ratings3).grid(row=5, column=1, 
                        sticky="nwe"))
        Label(self.frame, text="Rating:", font='Quicksand').grid(row=5,
              column=0, sticky="nwe")
        # calls the method results
        self.button = Button(self.frame, text="Recommendation!", 
                             command=self.results)
        self.button.grid(row=6, column=0, sticky="nwe")
        # make the correction button, calls the method learn
        self.correction = Button(self.frame, 
                                 text="Got bad rec?", 
                                 command=self.learn)
        self.correction.grid(row=7, column=0, sticky="nwe")

    def screenObjects(self):
        self.fontSize = 25
        self.font = 'Quicksand ' + str(self.fontSize) + ' bold'
        # hard code the center coordinates of each city we have data for
        self.pittsburgh = ('Pittsburgh', 40.4397, 79.9764)
        self.charlotte = ('Charlotte', 35.2269, 80.8433)
        self.urbana = ('Urbana', 40.1150, 88.2728)
        self.phoenix = ('Phoenix', 33.4500, 112.0667)
        self.vegas = ('Vegas', 36.1215, 115.1739)
        self.madison = ('Madison', 43.0667, 89.4000)
        self.cities = [self.pittsburgh, self.charlotte, self.urbana,
                       self.phoenix, self.vegas, self.madison]
        # find the city closest to your current location               
        self.city = finder.findClosestCity(self.cities)
        self.title = ('Which restaurants have you been to \n \t\tin ' +
                      self.city + '?')
        self.data = pd.read_csv('../clean/' + self.city + '.csv')
        self.marg = 10
        self.topMargin = self.fontSize + self.marg

    def canvasObjects(self):
        self.canvas.create_text(self.width/2, self.topMargin, text=self.title, 
                                font=self.font, anchor='center')
        self.canvas.create_line(self.marg, self.topMargin*2, self.width, 
                                self.topMargin*2, width=2, arrow=FIRST)
        self.recFontSize = 20
        self.recommendFont = 'Quicksand ' + str(self.recFontSize)
        self.canvas.create_text(self.width/2, self.height/4, text=
                                'You should definitely try...', 
                                font=self.recommendFont)

    def results(self):
        self.recommendation = ''
        # take the selections from the drop down boxes
        self.restaurants=[self.stvar.get(), self.stvar2.get(),self.stvar3.get()]
        self.ratings = [self.ratings1, self.ratings2, self.ratings3]
        # if all are selected then call the clustering algorithm code
        if self.restaurants == [s for s in self.restaurants if s]:
            self.recommendation = minwise.main([self.restaurants, self.ratings],
                                               self.data)
        self.recFontSize = 35
        self.recommendFont = 'Quicksand ' + str(self.recFontSize)+ ' bold'
        # redraw the results area in case we want a new recommendation
        # (just make a rectangle same color as background to draw over
        # everything)
        self.canvas.create_rectangle(0, self.height/3-15, 
                                     self.width, self.height, 
                                     fill=self.bg, width=0) 
        self.canvas.create_text(self.width/2, self.height/3, 
                                text=self.recommendation, font=
                                self.recommendFont, fill='maroon4')
        self.google()
        self.testset(self.restaurants, self.recommendation)

    def learn(self):
        # if the user didn't like the recommendation then add that combination
        # to the database
        # use that database for future recommendation
        corrections = open('learning.csv','a')
        corrections.write(str([self.restaurants, self.recommendation]).replace(
                          '[', '')+'\n')
        corrections.close()

    def testset(self, restaurants, recommendation):
        lines = []
        searchfile = open('../cluster/train.csv', 'r')
        for line in searchfile:
            lines.append(line)
        searchfile.close()
        cleaned = []
        for line in lines:
            cleaned.append(line.split(','))
        itarget = self.choices.index(recommendation)
        iothers = [self.choices.index(restaurants[0]), 
                   self.choices.index(restaurants[1]),
                   self.choices.index(restaurants[2])]        
        v1 = cleaned[itarget][iothers[0]]
        v2 = cleaned[itarget][iothers[1]]
        v3 = cleaned[itarget][iothers[2]]
        matchings = [v1, v2, v3]
        print matchings

    def google(self):
        # load the restaurant data to get the right info
        self.subset = self.data[['Name', 'Latitude', 'Longitude']]
        self.coordinates = self.subset[self.subset['Name'] == 
                                       self.recommendation].values.tolist()
        googlemap.makeMap(self.coordinates[0][1:])
        image = Image.open('map.jpg')
        photo = ImageTk.PhotoImage(image)
        label = Label(image=photo)
        label.image = photo
        # draw the google map picture on the canvas
        self.canvas.create_text(self.width/3-50, self.height/2-20, 
                                text='From you to there:', 
                                font='Quicksand 15 bold')
        self.canvas.create_image(self.width/3-50, self.height/2+100, 
                                 image=label.image)
        googlemap.directions(self.coordinates[0][1:])
        self.directions = googlemap.searchDirections()
        self.canvas.create_text(2*self.width/3, self.height/2-20, text=
                                'How to get there:', font='Quicksand 15 bold')
        # we have directions as a list, so print them on canvas here
        for idir in xrange(len(self.directions)):
            if len(self.directions[idir]) > 45:
                self.directions[idir] = self.directions[idir][:45] + '...'
            self.canvas.create_text(2*self.width/3, self.height/2+idir*12, 
                                    text=self.directions[idir], anchor='n',
                                    font='Quicksand')

    def ratings1(self, rating):
        # get the results of the slider bars
        self.ratings1 = rating
    def ratings2(self, rating):
        self.ratings2 = rating
    def ratings3(self, rating):
        self.ratings3 = rating
    
    def flatten(self, l):
        return sorted([element for sub in l for element in sub])
        
if __name__== '__main__':
    root=Tk()
    frame=Frame(root)
    gui=Engine(root, frame)
    root.mainloop()
