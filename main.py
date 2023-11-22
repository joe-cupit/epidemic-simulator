import worldmap as wm         # world map page
import diseaseselect as ds    # disease selection page
import globalvars as gb       # global variables
import simulation as sim      # the simulation modules

import tkinter as tk          # tkinter used for gui
from tkinter import ttk       # ttk used for more widgets on gui

import threading              # threads used in simulation
import time                   # used to vary simulation speeds
import json                   # json module used to load and save settings

from math import log


class App(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        # initializes the container for widgets on the gui
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.geometry(str(gb.WIDTH)+"x"+str(gb.HEIGHT))    # sets the width and height of the window
        self.resizable(False, False)                       # makes the window non-resizable
        self.title("Starting...")

        self.currentPage = MainPage       # saves the current page for use when pressing back arrows
        self.loadedfile = ""              # stores the name of the currently loaded file

        # loads and shows the starting window while all other windows initialize
        f = StartingScreen(container, self)
        f.grid(row=0, column=0, sticky="nsew")
        self.update()
        self.update_idletasks()

        # creates a dictoinary of classes for each window so they can be easily referenced and raised to main view
        self.frames = {}
        pages = (MainPage, SimulationSelectionPage, SettingsPage, DiseaseCompPage, LocationCompPage, PreventativeCompPage, SingleSimulationPage, wm.WorldMapPage, ds.DiseaseSelectionPage, ClosingScreen)
        for F in pages:
            frame = F(container, self)
            self.frames[F] = frame
        for F in self.frames:
            self.frames[F].grid(row=0, column=0, sticky="nsew")

        self.showPage(MainPage)
        self.title("Pandemic Simulator")

        # creates a menubar for the top of the window
        menubar = tk.Menu(container)
        # File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.createNewFile)
        filemenu.add_command(label="Load", command=self.loadSimFile)
        filemenu.add_command(label="Save", command=self.saveCurrentSettings)
        filemenu.add_command(label="Save As", command=self.saveAs)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)
        # Simulation Menu
        simmenu = tk.Menu(menubar, tearoff=0)
        simmenu.add_command(label="Home", command=lambda: self.showPage(MainPage))
        simmenu.add_command(label="Settings", command=lambda: self.showPage(SettingsPage))
        simmenu.add_separator()
        simmenu.add_command(label="Disease Comp", command=lambda: self.showPage(DiseaseCompPage))
        simmenu.add_command(label="Location Comp", command=lambda: self.showPage(LocationCompPage))
        simmenu.add_command(label="Prevent Comp", command=lambda: self.showPage(PreventativeCompPage))
        simmenu.add_command(label="Single Sim", command=lambda: self.showPage(SingleSimulationPage))
        menubar.add_cascade(label="Navigation", menu=simmenu)
        # Help Menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="How To", command=self.showHelp)
        menubar.add_cascade(label="Help", menu=helpmenu)
        tk.Tk.config(self, menu=menubar)       # adds the menu to the app

        # creates a style for the app so everything looks consistent
        simStyle = ttk.Style()
        simStyle.configure("TLabel", background=gb.bgcol)        # style for ttk.Label
        simStyle.configure("TFrame", background=gb.bgcol)        # style for ttk.Frame
        simStyle.configure("TScale", background=gb.bgcol)        # style for ttk.Scale
        simStyle.configure("TNotebook", background=gb.bgcol, border=0)                  # style for ttk.Notebook
        simStyle.configure("TCheckbutton", foreground="#09090A", background=gb.bgcol)   # style for ttk.Checkbutton

    def showPage(self, pageName):
        gb.return_frame = self.currentPage     # saves the previous frame so it can be easily returned to
        frame = self.frames[pageName]          # gets the new frame to be raise
        self.currentPage = pageName            # saves the new frames name as the current page
        frame.tkraise()                        # raises the new frame

    def close(self):
        # closing screen is displayed while other frames are destroyed below it
        self.showPage(ClosingScreen)
        self.title("Closing...")
        self.config(menu=tk.Menu(self))    # replaces the menu bar with an empty one

        self.update()
        self.update_idletasks()

        # loops through frames and destroys them from the app
        for frame in self.frames:
            self.frames[frame].grid_forget()
            self.frames[frame].destroy()

        self.destroy()

    def clearSimulationDiseases(self):
        # sets both simulation disease variables to none
        gb.simDisease1 = None
        gb.simDisease2 = None

    def clearSimulationLocations(self):
        # sets both simulation location variables to none
        gb.simLocation1 = None
        gb.simLocation2 = None

    def createNewFile(self):
        # clears simulation settings and resets the loaded file name
        self.clearSimulationLocations()
        self.clearSimulationDiseases()

        self.loadedfile = ""
        self.title("Pandemic Simulator")

    def saveCurrentSettings(self):
        if not self.loadedfile:              # if no file is currentrly open
            f = self.saveFileLocation()      # a new directory will be selected by the user
            if f is None:
                return                       # if no file was selected function returns
            self.loadedfile = f              # the selected file is assigned to the app loaded file variable

        # the country/disease name is saved if it exists, otherwise "None" is stored
        country1 = (gb.simLocation1.name if gb.simLocation1 else "None")
        country2 = (gb.simLocation2.name if gb.simLocation2 else "None")
        disease1 = (gb.simDisease1.name if gb.simDisease1 else "None")
        disease2 = (gb.simDisease2.name if gb.simDisease2 else "None")

        locations = [country1, country2]   # list of the names of current sim locations
        diseases = [disease1, disease2]    # list of the names of current sim diseases
        simcap = gb.simCapacity

        # dictionary object to be used to create json file
        data = {"simulation capacity": simcap, "locations": locations, "diseases": diseases}

        with open(self.loadedfile, "w") as f:       # opens the loaded file
            json.dump(data, f, indent=4)            # the dictionary is loaded into the file as json

        print("Saved File")

    def saveAs(self):
        filename = self.saveFileLocation()       # opens window to allow the user to select new file save location
        self.loadedfile = filename               # saves the file name
        self.saveCurrentSettings()               # saves the current settings to the location

    def saveFileLocation(self):
        # opens window to allow the user to select new file save location
        f = tk.filedialog.asksaveasfile(title="Save To", filetypes=[("Simulation", ".sim")], defaultextension=".sim")
        if f is None:
            return          # returns if no file is selected

        return f.name       # returns the filename of the selected file

    def loadSimFile(self):
        # opens window so the user can select a file to load
        f = tk.filedialog.askopenfilename(title="Open File", filetypes=[("Simulation", ".sim")])
        if not f:
            return                # returns if no file is selected
        self.loadSettings(f)      # if there is a file, its settings is loaded

    def loadSettings(self, filename):
        with open(filename) as f:         # opens a given filename
            data = json.load(f)           # loads the json file into a dictionary object

        simcap = data["simulation capacity"]
        gb.simCapacity = int(simcap)
        locations = data["locations"]                               # assigns the locations from the file to the global variables file
        gb.simLocation1 = self.getLocationByName(locations[0])      # gets the location object from the name
        gb.simLocation2 = self.getLocationByName(locations[1])      #
        diseases = data["diseases"]                                 # assigns the diseases from the file to the global variables file
        gb.simDisease1 = self.getDiseaseByName(diseases[0])         # gets the disease object from the name
        gb.simDisease2 = self.getDiseaseByName(diseases[1])         #

        name = filename.split("/")[-1]                  # gets only the name of the file out of its directory as a string
        self.title(f"Pandemic Simulator - {name}")      # sets the name of the window to show the currently opened file
        self.loadedfile = filename                      # changes the currently loaded file variable to the new filename

    def getLocationByName(self, location):
        # returns the location object given its name
        try:
            return wm.namecountrydict[location]      # if the location exists, the object is returned
        except KeyError:
            return None

    def getDiseaseByName(self, disease):
        # returns the disease object given its name
        for d in ds.disease_li:
            if d.name == disease:        # each spot in the disease list is checked for matching name
                return d                 # when an object matches it is returned
        return None                      # otherwise none is returned

    def showHelp(self):
        try:
            self.helppopup.destroy()      # if there is already a help pop-up, it will be destroyed before the new one is created
        except AttributeError:
            pass

        self.helppopup = tk.Toplevel(self.master)    # creates a new window for the help to be displayed in
        HelpPopup(self, self.helppopup)


class HelpPopup():

    def __init__(self, app, top):
        self.app = app                     # main app class
        self.top = top                     # window its displayed on
        self.top.resizable(False, False)   # non-resizable
        self.top.title("Help")

        # opens the help text file and displays the text on the screen
        with open("help-howto.txt", "r") as f:
            helptext = f.read()

        self.frame = ttk.Frame(self.top)
        tk.Message(self.frame, text=helptext, bg="white", justify="left", font=("Verdana", 9)).pack(padx=5, pady=5)
        self.frame.pack(expand=True)


class MainPage(ttk.Frame):

    def __init__(self, parent, app):
        ttk.Frame.__init__(self, parent)  # initalizes tkinter frame class
        self.app = app                    # base app class

        # creates the layout of title and navigation buttons
        title = ttk.Label(self, text="Epidemic Simulator", font=gb.TITLEFONT)
        title.place(relx=.5, rely=.15, anchor="n")

        button_frame = ttk.Frame(self)
        tk.Button(button_frame, text="Simulation", font=("Verdana", 24), width=14, command=lambda: app.showPage(SimulationSelectionPage)).pack(pady=3)
        tk.Button(button_frame, text="Settings", font=("Verdana", 16), width=9, command=lambda: app.showPage(SettingsPage)).pack(pady=3)
        tk.Button(button_frame, text="Exit", font=("Verdana", 16), width=9, command=app.close).pack(pady=3)
        button_frame.place(relx=0.5, rely=0.35, anchor="n")


class SimulationSelectionPage(ttk.Frame):

    def __init__(self, parent, app):
        ttk.Frame.__init__(self, parent)
        self.app = app

        # initializes layout with title and simulation type buttons that take the user to the relevant pages
        ttk.Label(self, text="Choose a simulation type:", font=gb.TITLEFONT).pack()

        button_frame = ttk.Frame(self)

        tk.Button(button_frame, text="Disease Comparison", width=21, font=gb.BIGFONT, command=lambda: app.showPage(DiseaseCompPage)).grid(row=0, column=0)
        txt = "Select two locations and compare the way a disease spreads in both locations side by side"
        tk.Message(button_frame, text=txt, width=600, font=gb.MEDFONT, bg=gb.bgcol).grid(row=0, column=1, sticky="w", pady=20, padx=20)

        tk.Button(button_frame, text="Location Comparison", width=21, font=gb.BIGFONT, command=lambda: app.showPage(LocationCompPage)).grid(row=1, column=0)
        txt = "Select two diseases and compare the way they spread in one location side by side"
        tk.Message(button_frame, text=txt, width=600, font=gb.MEDFONT, bg=gb.bgcol).grid(row=1, column=1, sticky="w", pady=20, padx=20)

        tk.Button(button_frame, text="Preventative Comparison", width=21, font=gb.BIGFONT, command=lambda: app.showPage(PreventativeCompPage)).grid(row=2, column=0)
        txt = "Select a disease and a location and compare how it spreads with different preventative methods side by side"
        tk.Message(button_frame, text=txt, width=600, font=gb.MEDFONT, bg=gb.bgcol).grid(row=2, column=1, sticky="w", pady=20, padx=20)

        tk.Button(button_frame, text="Single Simulation", width=21, font=gb.BIGFONT, command=lambda: app.showPage(SingleSimulationPage)).grid(row=3, column=0)
        txt = "Select a disease and a location and observe the way it spreads and develops overtime under selected conditions"
        tk.Message(button_frame, text=txt, width=600, font=gb.MEDFONT, bg=gb.bgcol).grid(row=3, column=1, sticky="w", pady=20, padx=20)

        button_frame.pack(pady=50)

        tk.Button(self, text="Back", command=lambda: app.showPage(MainPage)).pack()


class SettingsPage(ttk.Frame):

    def __init__(self, parent, app):
        ttk.Frame.__init__(self, parent)
        self.app = app

        # initializes the settings page
        ttk.Label(self, text="Settings", font=gb.TITLEFONT).pack()

        self.deafulttext = "None Selected"

        # string variables storing the simulation country/disease names
        self.locone = tk.StringVar(value="None Selected")
        self.loctwo = tk.StringVar(value="None Selected")
        self.disone = tk.StringVar(value="None Selected")
        self.distwo = tk.StringVar(value="None Selected")

        locdis = ttk.Label(self)    # frame for location and disease selection
        ttk.Label(locdis, text="Location Variables:", font=gb.BIGFONT).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(locdis, textvar=self.locone, font=gb.MEDFONT).grid(row=1, column=0, pady=2, sticky="w")
        ttk.Label(locdis, textvar=self.loctwo, font=gb.MEDFONT).grid(row=2, column=0, pady=2, sticky="w")

        ttk.Label(locdis, text="Disease Variables:", font=gb.BIGFONT).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Label(locdis, textvar=self.disone, font=gb.MEDFONT).grid(row=4, column=0, pady=2, sticky="w")
        ttk.Label(locdis, textvar=self.distwo, font=gb.MEDFONT).grid(row=5, column=0, pady=2, sticky="w")

        self.updateGlobalVars()    # updates the labels if any countries/diseases are already selected

        # edit buttons allow the user to edit each button
        # num = the number to be edited ; loc = boolean for if location is being edited
        for i in range(1, 3):
            tk.Button(locdis, text="Edit", command=lambda x=i: self.editVar(num=x, loc=True)).grid(row=i, column=1)
        for i in range(1, 3):
            tk.Button(locdis, text="Edit", command=lambda x=i: self.editVar(num=x, loc=False)).grid(row=i+3, column=1)

        locdis.pack(pady=30)

        # frame for controlling the simulation capacity
        simcapframe = ttk.Frame(self)
        ttk.Label(simcapframe, text="Simulation Capacity:", font=gb.BIGFONT).pack()
        self.simcapvalues = [1000, 5000, 10000, 25000, 50000, 75000, 100000, 250000, 500000, 1000000]
        self.simcap = tk.Scale(simcapframe, from_=min(self.simcapvalues), to=max(self.simcapvalues), command=self.simcapacitycallback, orient="horizontal")
        self.simcap.set(gb.simCapacity)
        self.simcap.pack()
        simcapframe.pack(pady=10)

        tk.Button(self, text="Back", command=lambda: app.showPage(MainPage)).pack()

        self.bind("<Expose>", self.updateGlobalVars)      # when the settings page is opened the variables are updated

    def simcapacitycallback(self, value):
        # makes sure the sim capacity slider is always at set values
        newvalue = min(self.simcapvalues, key=lambda x: abs(x-float(value)))   # finds the closest value to the current slider pos
        self.simcap.set(newvalue)
        gb.simCapacity = newvalue

    def updateGlobalVars(self, *args):
        # checks for the existence of loaction/disease objects and sets the names to the correct label on the settings page
        if c := gb.simLocation1:
            self.locone.set(c.name)
        else:
            self.locone.set(self.deafulttext)

        if c := gb.simLocation2:
            self.loctwo.set(c.name)
        else:
            self.loctwo.set(self.deafulttext)

        if d := gb.simDisease1:
            self.disone.set(d.name)
        else:
            self.disone.set(self.deafulttext)

        if d := gb.simDisease2:
            self.distwo.set(d.name)
        else:
            self.distwo.set(self.deafulttext)

        self.app.update_idletasks()

    def editVar(self, num=1, loc=False):
        gb.simEditing = num                # sets the variable number to be set

        if loc:
            self.app.showPage(wm.WorldMapPage)            # shows the world map to allow the user to select a country
        else:
            self.app.showPage(ds.DiseaseSelectionPage)    # shows the disease selection page to allow the user to select a disease


class SimulationPage(ttk.Frame):

    def __init__(self, parent, app):
        ttk.Frame.__init__(self, parent)  # initializes the tkinter frame class
        self.app = app                    # main app object

        self.bind("<Expose>", self.updateVars)   # calls updateVars everytime the page is openened

        self.simRunning = False     # boolean for if sim is currently running
        self.scale = False          # boolean for if graphs should be scaled
        self.loadedTime = 0         # int for how many timesteps have been loaded
        self.currentTime = 0        # int for currently displayed timestep

        # allows secondary thread to be used for simulation as tkinter gui updates can only happen on the main thread,
        self.setToDraw = tk.IntVar()                      # tkinter int var can be edited on secondary thread, then whenever
        self.setToDraw.trace("w", self.drawAllCanvas)     # it is edited the graphs are promted to update on the main thread

        self.simulationOne = sim.Simulation(gb.simLocation1, gb.simDisease1)   # stores simulation objects
        self.simulationTwo = sim.Simulation(gb.simLocation1, gb.simDisease2)

        self.figureOne = sim.SimulationFigure(self, self.simulationOne)        # stores figure objects
        self.figureTwo = sim.SimulationFigure(self, self.simulationTwo)
        self.canvasList = []

        self.simMainLabel = tk.StringVar()      # stores the name of the location/disease (depending on simulation type)
        self.simLabelOne = tk.StringVar()       # stores the name of the location/disaese relating to graph one /
        self.simLabelTwo = tk.StringVar()       # and graph two

        self.playlabel = tk.StringVar(value="▶")      # text on the play button

        self.scalegraph = tk.IntVar()                  # boolean controlling the scaling of the graphs
        self.scalegraph.set(1)
        self.scalegraph.trace("w", self.updateScale)

        self.useleg = tk.IntVar()                      # boolean controlling the legend on the graph
        self.useleg.set(1)
        self.useleg.trace("w", self.updateLeg)

        self.plotsus = tk.IntVar()                     # booleans controlling checkboxes for lines visible on the graphs
        self.plotsus.trace("w", self.updateVis)
        self.plotinf = tk.IntVar()
        self.plotinf.set(1)
        self.plotinf.trace("w", self.updateVis)
        self.plotrec = tk.IntVar()
        self.plotrec.trace("w", self.updateVis)
        self.plotmor = tk.IntVar()
        self.plotmor.trace("w", self.updateVis)
        self.plotnew = tk.IntVar()
        self.plotnew.set(1)
        self.plotnew.trace("w", self.updateVis)

        self.speedvalue = tk.DoubleVar(value=8)       # variable for speed the simulation plays, used in the slider

        # creates tkinter tabs to allow multiple layouts on the same page
        self.tabControl = ttk.Notebook(self)
        tab1 = ttk.Frame(self.tabControl)
        tab2 = ttk.Frame(self.tabControl)
        tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(tab1, text='Simulation View')
        self.tabControl.add(tab2, text='Simplified View')
        self.tabControl.add(tab3, text='Advanced View')
        self.tabControl.bind("<<NotebookTabChanged>>", self.drawAllCanvas)

        # initializes the layout of each tab
        self.simulationTab_init(tab1)
        self.simplifiedTab_init(tab2)
        self.advancedTab_init(tab3)

        # updates scale and variables for the page, bypass=True bypasses the check for a change in variables before updating
        self.updateVars(bypass=True)
        self.updateScale()

        tk.Button(self, text="🡰", width=6, command=self.back).place(x=10, y=10)    # creates a back button

    def simulationTab_init(self, tab):
        # sets the deafult layout for the simulation tab
        pagecanvas = []
        graph_frame = ttk.Frame(tab)
        graphOne = sim.DrawableCanvas(graph_frame, self.figureOne, (4, 3.3))
        graphOne.getCanvas().grid(row=1, column=0, columnspan=2)
        pagecanvas.append(graphOne)
        graphTwo = sim.DrawableCanvas(graph_frame, self.figureTwo, (4, 3.3))
        graphTwo.getCanvas().grid(row=1, column=2, columnspan=2)
        pagecanvas.append(graphTwo)
        self.canvasList.append(pagecanvas)

        self.setSimulationTitles(graph_frame, row=0, column=0)

        graph_frame.grid(pady=8, sticky="w")

        ctrl_frame = ttk.Frame(graph_frame)
        self.playPauseFrame(ctrl_frame).pack()
        self.resetLink = ttk.Label(ctrl_frame, text="Reset", font=("Calibri", 10, "underline"), cursor="hand2")
        self.resetLink.bind("<ButtonRelease-1>", self.resetSim)
        self.resetLink.pack(pady=5)
        ttk.Label(ctrl_frame, text="Sim Speed:", font=gb.SMLFONT).pack()
        speedslider = ttk.Scale(ctrl_frame, variable=self.speedvalue, orient="horizontal", from_=0.5, to=9.9, length=120)    # when logged gives values between 0.005s and 1.3s
        speedslider.pack()
        self.checkButtonFrame(ctrl_frame).pack(anchor="w", pady=15)

        ttk.Label(ctrl_frame, text="Starting Infected:").pack()
        self.startentry = tk.StringVar(value="10")
        self.startentry.trace("w", self.updateStartInf)
        ttk.Entry(ctrl_frame, textvar=self.startentry, width=7).pack()
        ctrl_frame.grid(row=1, column=4, rowspan=4, sticky="n", pady=5)

        self.simSettingsFrame(graph_frame)

    def simplifiedTab_init(self, tab):
        # sets the deafult layout for the simplified tab
        pagecanvas = []
        graph_frame = ttk.Frame(tab)
        graphOne = sim.DrawableCanvas(graph_frame, self.figureOne, (5, 4.65))
        graphOne.getCanvas().grid(row=1, column=0, columnspan=2)
        pagecanvas.append(graphOne)
        graphTwo = sim.DrawableCanvas(graph_frame, self.figureTwo, (5, 4.65))
        graphTwo.getCanvas().grid(row=1, column=2, columnspan=2)
        pagecanvas.append(graphTwo)
        self.canvasList.append(pagecanvas)
        graph_frame.pack(pady=3)

        self.setSimulationTitles(graph_frame, row=0, column=0)

        lowerframe = ttk.Frame(tab)
        lowerframe.pack(padx=36, anchor="n", fill="both")

        self.playPauseFrame(lowerframe).grid(row=0, column=0)

        self.checkButtonFrame(lowerframe, horizontal=True).grid(row=0, column=3, padx=30)

        speedslider = ttk.Scale(lowerframe, variable=self.speedvalue, orient="horizontal", from_=0.5, to=9.9, length=180)    # when logged gives values between 0.005s and 1.3s
        speedslider.grid(row=0, column=1, padx=50)

    def advancedTab_init(self, tab):
        # sets the deafult layout for the advanced tab
        pagecanvas = []
        graph_frame = ttk.Frame(tab)
        graphOne = sim.DrawableCanvas(graph_frame, self.figureOne, (3.8, 3.4))
        graphOne.getCanvas().grid(row=1, column=0, columnspan=2)
        pagecanvas.append(graphOne)
        graphTwo = sim.DrawableCanvas(graph_frame, self.figureTwo, (3.8, 3.4))
        graphTwo.getCanvas().grid(row=1, column=2, columnspan=2, padx=15)
        pagecanvas.append(graphTwo)
        self.canvasList.append(pagecanvas)

        self.setSimulationTitles(graph_frame, row=0, column=0)

        graph_frame.grid(pady=8, sticky="w")

        ctrl_frame = ttk.Frame(graph_frame)

        self.playPauseFrame(ctrl_frame).pack()

        self.resetLink = ttk.Label(ctrl_frame, text="Reset", font=("Calibri", 10, "underline"), cursor="hand2")
        self.resetLink.bind("<ButtonRelease-1>", self.resetSim)
        self.resetLink.pack(pady=5)

        ttk.Label(ctrl_frame, text="Sim Speed:", font=gb.SMLFONT).pack()
        speedslider = ttk.Scale(ctrl_frame, variable=self.speedvalue, orient="horizontal", from_=0.5, to=9.9, length=120)    # when logged gives values between 0.005s and 1.3s
        speedslider.pack()

        self.checkButtonFrame(ctrl_frame).pack(anchor="w", pady=15)
        ttk.Label(ctrl_frame, text="Starting Infected:").pack()
        self.startentry.trace("w", self.updateStartInf)
        ttk.Entry(ctrl_frame, textvar=self.startentry, width=7).pack()

        ctrl_frame.grid(row=1, column=4, sticky="n", pady=5, padx=15)

        info_frame1 = ttk.Frame(graph_frame)
        ttk.Label(info_frame1, text="New Cases:", font=("Verdana", 14)).grid(row=0, column=0, sticky="e")
        ttk.Label(info_frame1, text="Current Inf:", font=("Verdana", 14)).grid(row=1, column=0, sticky="e")
        ttk.Label(info_frame1, text="All Time Inf:", font=("Verdana", 14)).grid(row=2, column=0, sticky="e")
        ttk.Label(info_frame1, text="Recovered:", font=("Verdana", 14)).grid(row=3, column=0, sticky="e")
        ttk.Label(info_frame1, text="Deaths:", font=("Verdana", 14)).grid(row=4, column=0, sticky="e")
        self.adv_newcases_1 = tk.StringVar()
        self.adv_current_1 = tk.StringVar()
        self.adv_alltime_1 = tk.StringVar()
        self.adv_recovered_1 = tk.StringVar()
        self.adv_deaths_1 = tk.StringVar()
        ttk.Label(info_frame1, textvar=self.adv_newcases_1, font=("Verdana", 14)).grid(row=0, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_current_1, font=("Verdana", 14)).grid(row=1, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_alltime_1, font=("Verdana", 14)).grid(row=2, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_recovered_1, font=("Verdana", 14)).grid(row=3, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_deaths_1, font=("Verdana", 14)).grid(row=4, column=1, sticky="w")
        info_frame1.grid(row=2, column=0)

        info_frame1 = ttk.Frame(graph_frame)
        ttk.Label(info_frame1, text="New Cases:", font=("Verdana", 14)).grid(row=0, column=0, sticky="e")
        ttk.Label(info_frame1, text="Current Inf:", font=("Verdana", 14)).grid(row=1, column=0, sticky="e")
        ttk.Label(info_frame1, text="All Time Inf:", font=("Verdana", 14)).grid(row=2, column=0, sticky="e")
        ttk.Label(info_frame1, text="Recovered:", font=("Verdana", 14)).grid(row=3, column=0, sticky="e")
        ttk.Label(info_frame1, text="Deaths:", font=("Verdana", 14)).grid(row=4, column=0, sticky="e")
        self.adv_newcases_2 = tk.StringVar()
        self.adv_current_2 = tk.StringVar()
        self.adv_alltime_2 = tk.StringVar()
        self.adv_recovered_2 = tk.StringVar()
        self.adv_deaths_2 = tk.StringVar()
        ttk.Label(info_frame1, textvar=self.adv_newcases_2, font=("Verdana", 14)).grid(row=0, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_current_2, font=("Verdana", 14)).grid(row=1, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_alltime_2, font=("Verdana", 14)).grid(row=2, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_recovered_2, font=("Verdana", 14)).grid(row=3, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_deaths_2, font=("Verdana", 14)).grid(row=4, column=1, sticky="w")
        info_frame1.grid(row=2, column=2)

        self.updateAdvanced()

    def updateAdvanced(self):
        # gets advanced data for both simulations and updates the string variables
        t = self.currentTime
        self.adv_newcases_1.set(self.figureOne.simulation.newplot[t])
        self.adv_current_1.set(self.figureOne.simulation.infplot[t])
        self.adv_alltime_1.set(sum(self.figureOne.simulation.newplot[:t+1])+self.figureOne.simulation.infplot[0])
        self.adv_recovered_1.set(self.figureOne.simulation.recplot[t])
        self.adv_deaths_1.set(self.figureOne.simulation.morplot[t])

        self.adv_newcases_2.set(self.figureTwo.simulation.newplot[t])
        self.adv_current_2.set(self.figureTwo.simulation.infplot[t])
        self.adv_alltime_2.set(sum(self.figureTwo.simulation.newplot[:t+1])+self.figureOne.simulation.infplot[0])
        self.adv_recovered_2.set(self.figureTwo.simulation.recplot[t])
        self.adv_deaths_2.set(self.figureTwo.simulation.morplot[t])

    def playPauseFrame(self, frame):
        # creates a frame for controlling the playback of the simulation
        buttonframe = ttk.Frame(frame, cursor="hand2")
        first = ttk.Label(buttonframe, text="⏮", font=("Verdana", 15))
        first.bind("<ButtonRelease-1>", self.firstTimestep)
        first.grid(row=0, column=0)
        prv = ttk.Label(buttonframe, text="⏪", font=("Verdana", 15))
        prv.bind("<ButtonRelease-1>", self.prevTimestep)
        prv.grid(row=0, column=1)
        play = ttk.Label(buttonframe, textvar=self.playlabel, font=("Verdana", 15))
        play.bind("<ButtonRelease-1>", self.playPauseButton)
        play.grid(row=0, column=2)
        nxt = ttk.Label(buttonframe, text="⏩", font=("Verdana", 15))
        nxt.bind("<ButtonRelease-1>", lambda e, b=True: self.nextTimestep(button=b))
        nxt.grid(row=0, column=3)
        last = ttk.Label(buttonframe, text="⏭", font=("Verdana", 15))
        last.bind("<ButtonRelease-1>", self.lastTimestep)
        last.grid(row=0, column=4)
        return buttonframe

    def checkButtonFrame(self, frame, horizontal=False):
        # creates the layout for the simulation control checkbuttons
        checkframe = ttk.Frame(frame)

        # creates list of rows and columns for the checkbuttons
        r = range(7)
        c = [0] * 7
        if horizontal:
            r, c = c, r        # flips rows and columns if checkframe is to be horizontal

        ttk.Checkbutton(checkframe, text="Scale Graph", variable=self.scalegraph).grid(row=r[0], column=c[0], sticky="w")
        if not horizontal:
            ttk.Checkbutton(checkframe, text="Use Legend", variable=self.useleg).grid(row=r[1], column=c[1], pady=5, sticky="w")
        ttk.Checkbutton(checkframe, text="Susceptible", variable=self.plotsus).grid(row=r[2], column=c[2], sticky="w")
        ttk.Checkbutton(checkframe, text="Infectious", variable=self.plotinf).grid(row=r[3], column=c[3], sticky="w")
        ttk.Checkbutton(checkframe, text="Recovered", variable=self.plotrec).grid(row=r[4], column=c[4], sticky="w")
        ttk.Checkbutton(checkframe, text="Deaths", variable=self.plotmor).grid(row=r[5], column=c[5], sticky="w")
        ttk.Checkbutton(checkframe, text="New Cases", variable=self.plotnew).grid(row=r[6], column=c[6], sticky="w")
        return checkframe

    def simSettingsFrame(self, frame):
        # creates a frame for displaying preventative measures the user can control
        simframe = ttk.Frame(frame)

        ttk.Label(simframe, text="Preventative Measures:", font=gb.BIGFONT).grid(row=0, column=0, columnspan=4, pady=10)

        self.usevacc = tk.BooleanVar()
        self.usevacc.trace("w", self.updateVacc)
        self.vaccbutt = ttk.Checkbutton(simframe, text="Activate Vaccinations", variable=self.usevacc)
        self.vaccbutt.grid(row=1, column=0, columnspan=2)
        ttk.Label(simframe, text="Vaccination Percent:", font=gb.MEDFONT).grid(row=2, column=0, columnspan=2)
        self.vaccper = tk.DoubleVar()
        self.vaccper.trace("w", self.updateVacc)
        self.vaccscale = ttk.Scale(simframe, variable=self.vaccper, orient="horizontal", from_=0, to=1, length=80, state="disabled")
        self.vaccscale.grid(row=3, column=0)
        self.vacclab = tk.StringVar(value="0.0%")
        ttk.Label(simframe, textvar=self.vacclab, font=gb.MEDFONT).grid(row=3, column=1)
        self.updateVacc()

        self.usequar = tk.BooleanVar()
        self.usequar.trace("w", self.updateQuar)
        self.quarbutt = ttk.Checkbutton(simframe, text="Activate Quarantine", variable=self.usequar)
        self.quarbutt.grid(row=1, column=2, padx=80)
        ttk.Label(simframe, text="Quarantining Level:", font=gb.MEDFONT).grid(row=2, column=2)
        self.quarlvl = tk.DoubleVar(value=.5)
        self.quarlvl.trace("w", self.updateQuar)
        self.quarscale = ttk.Scale(simframe, variable=self.quarlvl, orient="horizontal", from_=.1, to=.6, length=80, state="disabled")
        self.quarscale.grid(row=3, column=2)
        self.updateQuar()

        self.uselock = tk.BooleanVar()
        self.uselock.trace("w", self.updateLock)
        self.lockbutt = ttk.Checkbutton(simframe, text="Use Lockdowns", variable=self.uselock)
        self.lockbutt.grid(row=1, column=3)
        ttk.Label(simframe, text="Lockdown Intensity:", font=gb.MEDFONT).grid(row=2, column=3)
        self.locklvl = tk.DoubleVar(value=.1)
        self.locklvl.trace("w", self.updateLock)
        self.lockscale = ttk.Scale(simframe, variable=self.locklvl, orient="horizontal", from_=.6, to=0, length=80, state="disabled")
        self.lockscale.grid(row=3, column=3)
        self.updateLock()

        simframe.grid(row=4, column=0, columnspan=4, pady=5)

    def updateVis(self, *a):
        # updates the list controlling visibility of plots on the graph when a checkbox is changed
        viewplot = [self.plotsus.get(), self.plotinf.get(), self.plotrec.get(), self.plotmor.get(), self.plotnew.get()]
        self.figureOne.setVisible(viewplot)
        self.figureTwo.setVisible(viewplot)
        self.refreshScale()
        self.drawGraphs()

    def updateScale(self, *a):
        # updates the boolean controlling the scale of the graph when the checkbox is changed
        self.scale = self.scalegraph.get()
        self.refreshScale()
        self.drawGraphs()

    def updateLeg(self, *a):
        # updates the boolean controlling the visibility of the graph legends when the checkbox is changed
        uselegend = self.useleg.get()
        self.figureOne.uselegend = uselegend
        self.figureOne.updateLegend()
        self.figureTwo.uselegend = uselegend
        self.figureTwo.updateLegend()
        self.drawGraphs()

    def updateStartInf(self, *a):
        # changes the starting infected for both simulations when it is changed
        startinf = self.startentry.get()
        if startinf:
            # uses validation to make sure the entry is only digits and the length is less than 6
            if not startinf[-1].isdecimal() or len(startinf) > 5:
                self.startentry.set(startinf[:-1])
            else:
                self.simulationOne.startinf = int(startinf)
                self.simulationTwo.startinf = int(startinf)

    def updateVacc(self, *a):
        # updates the vaccination percentage for both simulations when the checkbox/slider is changed
        if self.usevacc.get():
            vaccper = self.vaccper.get()
            self.vaccscale["state"] = "normal"
            vaccstr = f"{round(vaccper*100, 1)}%"
            self.vacclab.set(vaccstr)
        else:
            vaccper = 0
            self.vaccscale["state"] = "disabled"
        self.simulationOne.vaccinated_perc = vaccper
        self.simulationTwo.vaccinated_perc = vaccper

    def updateQuar(self, *a):
        # updates the quarantine level for both simulations when the checkbox/slider is changed
        usequar = self.usequar.get()
        self.simulationOne.usequarantine = usequar
        self.simulationTwo.usequarantine = usequar
        if usequar:
            quarlvl = self.quarlvl.get()
            self.simulationOne.quarantine_lvl = quarlvl
            self.simulationTwo.quarantine_lvl = quarlvl
            self.quarscale["state"] = "normal"
        else:
            self.quarscale["state"] = "disabled"

    def updateLock(self, *a):
        # updates the lockdown intensity for both simulations when the checkbox/slider is changed
        uselock = self.uselock.get()
        self.simulationOne.uselockdown = uselock
        self.simulationTwo.uselockdown = uselock
        if uselock:
            locklvl = self.locklvl.get()
            self.simulationOne.lockdown_proportion = locklvl
            self.simulationTwo.lockdown_proportion = locklvl
            self.lockscale["state"] = "normal"
        else:
            self.lockscale["state"] = "disabled"

    def disableSliders(self, running=False):
        # updates the visibility of sliders based on their activity and if the sim is running
        if running:
            state = "disabled"
            self.vaccbutt["state"] = state
            self.vaccscale["state"] = state
            self.quarbutt["state"] = state
            self.quarscale["state"] = state
            self.lockbutt["state"] = state
            self.lockscale["state"] = state
        else:
            state = "normal"
            self.vaccbutt["state"] = state
            self.quarbutt["state"] = state
            self.lockbutt["state"] = state
            self.updateVacc()
            self.updateQuar()
            self.updateLock()

    def configMaxPlot(self, viewplot, plots):
        # finds the max value in all the visible plots
        maxplot = 0
        for i in range(len(viewplot)):
            if viewplot[i] and max(plots[i]) > maxplot:
                maxplot = max(plots[i])

        if maxplot < 46:
            return 50        # minimum y scale up to 50
        else:
            return int(maxplot * 1.1)    # max increased so there is room above the plots

    def refreshScale(self):
        # sets the scale for both figures based on if they should be the same
        max1 = self.figureOne.getMaxPoint()
        max2 = self.figureTwo.getMaxPoint()
        if self.scale:
            if max1 > max2:
                maxplot = max1
            else:
                maxplot = max2
            self.figureOne.configLimit(maxplot)
            self.figureTwo.configLimit(maxplot)
        else:
            self.figureOne.configLimit(max1)
            self.figureTwo.configLimit(max2)

    def playPauseButton(self, *a):
        if self.simulationOne.runnable and self.simulationTwo.runnable:     # only runs when both simulations can be started
            if self.simRunning:               # if the simulation is already running
                self.simRunning = False       # the simulation is stopped
                self.disableSliders(running=False)
                self.playlabel.set("▶")       # and the button is set to a play symbol
            else:                             # if the simulation is not running
                self.simRunning = True        # the simulation is started
                self.disableSliders(running=True)
                self.playlabel.set("⏸")      # and the button is set to a pause symbol

                interval = 1 - log(self.speedvalue.get(), 10)    # the time interval between each step in the simulation calculated with the slider
                simthread = threading.Thread(target=lambda: self.runSimulation(interval=interval))      # a thread is created, running the simulation
                simthread.daemon = True        # set to daemon, so if the main program stops running, the thread will be killed
                simthread.start()              # the thread is started

    def runSimulation(self, interval=1):
        while self.simRunning:            # the thread is set to loop infinitely while the simulation is set to play
            self.nextTimestep()           # the next timestep is calculated
            time.sleep(interval)          # thread sleeps to allow for chosen interval

    def nextTimestep(self, button=False, *a):
        # button=True when the next timestep button is clicked which can only pass if the simulation is not running
        if self.simRunning != button:           # (sim running) XOR (next button clicked); allows next timestep to be calculated if only one is true
            self.currentTime += 1               # sim timestep is updated
            self.figureOne.nextTimestep()       # next timestep calculated for first sim
            self.figureTwo.nextTimestep()       # next timestep calculated for second sim
            self.drawGraphs()                   # both graphs are updated

    def prevTimestep(self, *a):
        # shows the simulation up to the previous timestep
        if self.simRunning:
            self.playPauseButton()    # simulation is paused if it is running
        self.currentTime -= 1
        if self.currentTime < 0:      # minimum timestep is 0
            self.currentTime = 0
        self.drawGraphs()

    def firstTimestep(self, *a):
        # graphs go back to display the first timestep
        if self.simRunning:
            self.playPauseButton()    # simulation is paused
        self.currentTime = 0
        self.drawGraphs()

    def lastTimestep(self, *a):
        # simulation displays everything up to the last loaded timestep
        self.currentTime = self.figureOne.loadedTimesteps - 1
        self.drawGraphs()

    def resetSim(self, *a):
        # resets the simulations and their figures
        if self.simRunning:
            self.playPauseButton()   # pauses the simulation first
        self.loadedTime = 0
        self.currentTime = 0
        self.figureOne.resetSim()
        self.figureTwo.resetSim()
        self.drawGraphs()
        self.updateAdvanced()

    def drawGraphs(self):
        # updates both graphs
        self.figureOne.updateGraph()
        self.figureTwo.updateGraph()
        self.refreshScale()
        self.setToDraw.set(1)     # prompts the graphs to draw on screen

    def drawAllCanvas(self, *a):
        # loops through all canvas objects that are on the currently selected tab and draws them onto the screen
        canvasid = self.tabControl.index(self.tabControl.select())
        for c in self.canvasList[canvasid]:
            c.draw()

        if canvasid == 2:
            self.updateAdvanced()     # if the advanced tab is selected the advanced data is updated

    def editVar(self, num=1, loc=False):
        # edits a simulation variable, num=the number of the variable being edited (1 or 2) and loc is true when editing a location
        gb.simEditing = num

        if loc:
            self.app.showPage(wm.WorldMapPage)
        else:
            self.app.showPage(ds.DiseaseSelectionPage)

    def back(self):
        # shows the simulation selection page
        self.app.showPage(SimulationSelectionPage)


class DiseaseCompPage(SimulationPage):

    def __init__(self, parent, app):
        super().__init__(parent, app)     # initializes the deafult simulation page

        # adds the location edit option at the top of the window
        self.countryframe = ttk.Frame(self)
        ttk.Label(self.countryframe, text="Simulating in", font=("Verdana", 21)).grid(row=0, column=0)
        ttk.Label(self.countryframe, textvar=self.simMainLabel, font=("Verdana", 21, "bold")).grid(row=0, column=1, padx=8)
        countryedit = ttk.Label(self.countryframe, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        countryedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=True: self.editVar(num=i, loc=loc))
        countryedit.grid(row=0, column=2, sticky="s", padx=4, pady=5)
        self.countryframe.pack()

        self.tabControl.pack(padx=3, pady=2, expand=1, fill="both")

    def setSimulationTitles(self, frame, row=0, column=0):
        # adds disease titles and edit buttons to the window
        ttk.Label(frame, textvar=self.simLabelOne, font=("Verdana", 16, "bold")).grid(row=0, column=0, sticky="e")
        diseaseoneedit = ttk.Label(frame, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        diseaseoneedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=False: self.editVar(num=i, loc=loc))
        diseaseoneedit.grid(row=0, column=1, sticky="sw", padx=4, pady=5)
        ttk.Label(frame, textvar=self.simLabelTwo, font=("Verdana", 16, "bold")).grid(row=0, column=2, sticky="e")
        diseasetwoedit = ttk.Label(frame, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        diseasetwoedit.bind("<ButtonRelease-1>", lambda e, i=2, loc=False: self.editVar(num=i, loc=loc))
        diseasetwoedit.grid(row=0, column=3, sticky="sw", padx=4, pady=5)

    def updateVars(self, *a, bypass=False):
        # updates the simulation varaibles if they have changed
        country = gb.simLocation1
        disease1 = gb.simDisease1
        disease2 = gb.simDisease2

        if self.varsChanged(country, disease1, disease2) or bypass:
            # changes the objects in each simulation
            self.simulationOne.setLocation(country)
            self.simulationTwo.setLocation(country)
            self.simulationOne.setDisease(disease1)
            self.simulationTwo.setDisease(disease2)

            # updates the titles of the graphs
            if country:
                self.simMainLabel.set(country.name)
            else:
                self.simMainLabel.set("[None Selected]")
            if disease1:
                self.simLabelOne.set(disease1.name)
            else:
                self.simLabelOne.set("[None Selected]")
            if disease2:
                self.simLabelTwo.set(disease2.name)
            else:
                self.simLabelTwo.set("[None Selected]")

            self.resetSim()

    def varsChanged(self, newcountry, newdisease1, newdisease2):
        # returns true if any object does not match the currently selected object
        if newcountry != self.simulationOne.country:
            return True
        if newdisease1 != self.simulationOne.disease:
            return True
        if newdisease2 != self.simulationTwo.disease:
            return True

        return False


class LocationCompPage(SimulationPage):

    def __init__(self, parent, app):
        super().__init__(parent, app)      # initializes the deafult simulation page

        # adds the disease edit option at the top of the window
        self.diseaseframe = ttk.Frame(self)
        ttk.Label(self.diseaseframe, text="Simulating", font=("Verdana", 21)).grid(row=0, column=0)
        ttk.Label(self.diseaseframe, textvar=self.simMainLabel, font=("Verdana", 21, "bold")).grid(row=0, column=1, padx=8)
        countryedit = ttk.Label(self.diseaseframe, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        countryedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=False: self.editVar(num=i, loc=loc))
        countryedit.grid(row=0, column=2, sticky="s", padx=4, pady=5)
        self.diseaseframe.pack()

        self.tabControl.pack(padx=3, pady=2, expand=1, fill="both")

    def setSimulationTitles(self, frame, row=0, column=0):
        # adds location titles and edit buttons to the window
        ttk.Label(frame, textvar=self.simLabelOne, font=("Verdana", 16, "bold")).grid(row=0, column=0, sticky="e")
        locationoneedit = ttk.Label(frame, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        locationoneedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=True: self.editVar(num=i, loc=loc))
        locationoneedit.grid(row=0, column=1, sticky="sw", padx=4, pady=5)
        ttk.Label(frame, textvar=self.simLabelTwo, font=("Verdana", 16, "bold")).grid(row=0, column=2, sticky="e")
        locationtwoedit = ttk.Label(frame, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        locationtwoedit.bind("<ButtonRelease-1>", lambda e, i=2, loc=True: self.editVar(num=i, loc=loc))
        locationtwoedit.grid(row=0, column=3, sticky="sw", padx=4, pady=5)

    def updateVars(self, *a, bypass=False):
        # updates the simulation varaibles if they have changed
        disease = gb.simDisease1
        country1 = gb.simLocation1
        country2 = gb.simLocation2

        if self.varsChanged(disease, country1, country2) or bypass:
            # changes the objects in each simulation
            self.simulationOne.setLocation(country1)
            self.simulationTwo.setLocation(country2)
            self.simulationOne.setDisease(disease)
            self.simulationTwo.setDisease(disease)

            # updates the titles of the graphs
            if disease:
                self.simMainLabel.set(disease.name)
            else:
                self.simMainLabel.set("[None Selected]")
            if country1:
                self.simLabelOne.set(country1.name)
            else:
                self.simLabelOne.set("[None Selected]")
            if country2:
                self.simLabelTwo.set(country2.name)
            else:
                self.simLabelTwo.set("[None Selected]")

            self.resetSim()

    def varsChanged(self, newdisease, newcountry1, newcountry2):
        # returns true if any object does not match the currently selected object
        if newdisease != self.simulationOne.disease:
            return True
        if newcountry1 != self.simulationOne.country:
            return True
        if newcountry2 != self.simulationTwo.country:
            return True

        return False


class PreventativeCompPage(SimulationPage):

    def __init__(self, parent, app):
        super().__init__(parent, app)      # initializes the deafult simulation page

        # creates a title with disease and location and relevant edit buttons
        self.titleframe = ttk.Frame(self)
        ttk.Label(self.titleframe, text="Simulating", font=("Verdana", 21)).grid(row=0, column=0, padx=5)
        ttk.Label(self.titleframe, textvar=self.simMainLabel, font=("Verdana", 21, "bold")).grid(row=0, column=1)
        diseaseedit = ttk.Label(self.titleframe, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        diseaseedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=False: self.editVar(num=i, loc=loc))
        diseaseedit.grid(row=0, column=2, sticky="s", padx=4, pady=5)

        ttk.Label(self.titleframe, text="in", font=("Verdana", 21)).grid(row=0, column=3, padx=5)
        ttk.Label(self.titleframe, textvar=self.simLabelOne, font=("Verdana", 21, "bold")).grid(row=0, column=4)
        countryedit = ttk.Label(self.titleframe, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        countryedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=True: self.editVar(num=i, loc=loc))
        countryedit.grid(row=0, column=5, sticky="s", padx=4, pady=5)
        self.titleframe.pack()

        self.tabControl.pack(padx=3, pady=2, expand=1, fill="both")

    def setSimulationTitles(self, frame, row=0, column=0):
        ttk.Label(frame, text="Sim One", font=("Verdana", 16, "bold")).grid(row=0, column=0, sticky="e")
        ttk.Label(frame, text="Sim Two", font=("Verdana", 16, "bold")).grid(row=0, column=2, sticky="e")

    def simSettingsFrame(self, frame):
        # overrides the deafult preventative measures layout to add two control sections
        simframe = ttk.Frame(frame)
        ttk.Label(simframe, text="Preventative Measures:", font=gb.MEDFONT).grid(row=0, column=0, columnspan=4, pady=5)

        tmpframe = ttk.Frame(simframe)

        self.usevacc = tk.BooleanVar()
        self.usevacc.trace("w", self.updateVacc)
        self.vaccbutt = ttk.Checkbutton(tmpframe, text="Activate Vaccinations", variable=self.usevacc)
        self.vaccbutt.grid(row=1, column=0, columnspan=2)
        ttk.Label(tmpframe, text="Vaccination Percent:", font=gb.SMLFONT).grid(row=2, column=0, columnspan=2)
        self.vaccper = tk.DoubleVar()
        self.vaccper.trace("w", self.updateVacc)
        self.vaccscale = ttk.Scale(tmpframe, variable=self.vaccper, orient="horizontal", from_=0, to=1, length=80, state="disabled")
        self.vaccscale.grid(row=3, column=0)
        self.vacclab = tk.StringVar(value="0.0%")
        ttk.Label(tmpframe, textvar=self.vacclab, font=gb.SMLFONT).grid(row=3, column=1)

        self.usequar = tk.BooleanVar()
        self.usequar.trace("w", self.updateQuar)
        self.quarbutt = ttk.Checkbutton(tmpframe, text="Activate Quarantine", variable=self.usequar)
        self.quarbutt.grid(row=1, column=2, padx=40)
        ttk.Label(tmpframe, text="Quarantining Level:", font=gb.SMLFONT).grid(row=2, column=2)
        self.quarlvl = tk.DoubleVar(value=.5)
        self.quarlvl.trace("w", self.updateQuar)
        self.quarscale = ttk.Scale(tmpframe, variable=self.quarlvl, orient="horizontal", from_=.1, to=.6, length=80, state="disabled")
        self.quarscale.grid(row=3, column=2)

        self.uselock = tk.BooleanVar()
        self.uselock.trace("w", self.updateLock)
        self.lockbutt = ttk.Checkbutton(tmpframe, text="Use Lockdowns", variable=self.uselock)
        self.lockbutt.grid(row=4, column=0, columnspan=3)
        ttk.Label(tmpframe, text="Lockdown Intensity:", font=gb.SMLFONT).grid(row=5, column=0, columnspan=3)
        self.locklvl = tk.DoubleVar(value=.1)
        self.locklvl.trace("w", self.updateLock)
        self.lockscale = ttk.Scale(tmpframe, variable=self.locklvl, orient="horizontal", from_=.6, to=0, length=80, state="disabled")
        self.lockscale.grid(row=6, column=0, columnspan=3)

        tmpframe.grid(row=1, column=0, columnspan=2, padx=50)
        tmpframe2 = ttk.Frame(simframe)

        self.usevacc2 = tk.BooleanVar()
        self.usevacc2.trace("w", self.updateVacc)
        self.vaccbutt2 = ttk.Checkbutton(tmpframe2, text="Activate Vaccinations", variable=self.usevacc2)
        self.vaccbutt2.grid(row=1, column=0, columnspan=2)
        ttk.Label(tmpframe2, text="Vaccination Percent:", font=gb.SMLFONT).grid(row=2, column=0, columnspan=2)
        self.vaccper2 = tk.DoubleVar()
        self.vaccper2.trace("w", self.updateVacc)
        self.vaccscale2 = ttk.Scale(tmpframe2, variable=self.vaccper2, orient="horizontal", from_=0, to=1, length=80, state="disabled")
        self.vaccscale2.grid(row=3, column=0)
        self.vacclab2 = tk.StringVar(value="0.0%")
        ttk.Label(tmpframe2, textvar=self.vacclab2, font=gb.SMLFONT).grid(row=3, column=1)

        self.usequar2 = tk.BooleanVar()
        self.usequar2.trace("w", self.updateQuar)
        self.quarbutt2 = ttk.Checkbutton(tmpframe2, text="Activate Quarantine", variable=self.usequar2)
        self.quarbutt2.grid(row=1, column=2, padx=40)
        ttk.Label(tmpframe2, text="Quarantining Level:", font=gb.SMLFONT).grid(row=2, column=2)
        self.quarlvl2 = tk.DoubleVar(value=.5)
        self.quarlvl2.trace("w", self.updateQuar)
        self.quarscale2 = ttk.Scale(tmpframe2, variable=self.quarlvl2, orient="horizontal", from_=.1, to=.6, length=80, state="disabled")
        self.quarscale2.grid(row=3, column=2)

        self.uselock2 = tk.BooleanVar()
        self.uselock2.trace("w", self.updateLock)
        self.lockbutt2 = ttk.Checkbutton(tmpframe2, text="Use Lockdowns", variable=self.uselock2)
        self.lockbutt2.grid(row=4, column=0, columnspan=3)
        ttk.Label(tmpframe2, text="Lockdown Intensity:", font=gb.SMLFONT).grid(row=5, column=0, columnspan=3)
        self.locklvl2 = tk.DoubleVar(value=.1)
        self.locklvl2.trace("w", self.updateLock)
        self.lockscale2 = ttk.Scale(tmpframe2, variable=self.locklvl2, orient="horizontal", from_=.6, to=0, length=80, state="disabled")
        self.lockscale2.grid(row=6, column=0, columnspan=3)

        tmpframe2.grid(row=1, column=2, columnspan=2)
        simframe.grid(row=4, column=0, columnspan=4)

        self.updateVacc()
        self.updateQuar()
        self.updateLock()

    def updateVacc(self, *a):
        # overrides the deafult function to update each simulation separately
        if self.usevacc.get():
            vaccper = self.vaccper.get()
            self.vaccscale["state"] = "normal"
            vaccstr = f"{round(vaccper*100, 1)}%"
            self.vacclab.set(vaccstr)
        else:
            vaccper = 0
            self.vaccscale["state"] = "disabled"
        self.simulationOne.vaccinated_perc = vaccper

        if self.usevacc2.get():
            vaccper2 = self.vaccper2.get()
            self.vaccscale2["state"] = "normal"
            vaccstr2 = f"{round(vaccper2*100, 1)}%"
            self.vacclab2.set(vaccstr2)
        else:
            vaccper2 = 0
            self.vaccscale2["state"] = "disabled"
        self.simulationTwo.vaccinated_perc = vaccper2

    def updateQuar(self, *a):
        # overrides the deafult function to update each simulation separately
        usequar = self.usequar.get()
        self.simulationOne.usequarantine = usequar
        if usequar:
            quarlvl = self.quarlvl.get()
            self.simulationOne.quarantine_lvl = quarlvl
            self.quarscale["state"] = "normal"
        else:
            self.quarscale["state"] = "disabled"

        usequar2 = self.usequar2.get()
        self.simulationTwo.usequarantine = usequar2
        if usequar2:
            quarlvl2 = self.quarlvl2.get()
            self.simulationTwo.quarantine_lvl = quarlvl2
            self.quarscale2["state"] = "normal"
        else:
            self.quarscale2["state"] = "disabled"

    def updateLock(self, *a):
        # overrides the deafult function to update each simulation separately
        uselock = self.uselock.get()
        self.simulationOne.uselockdown = uselock
        if uselock:
            locklvl = self.locklvl.get()
            self.simulationOne.lockdown_proportion = locklvl
            self.lockscale["state"] = "normal"
        else:
            self.lockscale["state"] = "disabled"

        uselock2 = self.uselock2.get()
        self.simulationTwo.uselockdown = uselock2
        if uselock2:
            locklvl2 = self.locklvl.get()
            self.simulationTwo.lockdown_proportion = locklvl2
            self.lockscale2["state"] = "normal"
        else:
            self.lockscale2["state"] = "disabled"

    def disableSliders(self, running=False):
        # performs the same as parent function but for the newly added sliders/checkbutons, then calls parent function
        if running:
            state = "disabled"
            self.vaccbutt2["state"] = state
            self.vaccscale2["state"] = state
            self.quarbutt2["state"] = state
            self.quarscale2["state"] = state
            self.lockbutt2["state"] = state
            self.lockscale2["state"] = state
        else:
            state = "normal"
            self.vaccbutt2["state"] = state
            self.quarbutt2["state"] = state
            self.lockbutt2["state"] = state
            self.updateVacc()
            self.updateQuar()
            self.updateLock()
        super().disableSliders(running=running)          # runs the disableSliders function of the parent class

    def updateVars(self, *a, bypass=False):
        # updates the simulation varaibles if they have changed
        disease = gb.simDisease1
        country = gb.simLocation1

        if self.varsChanged(disease, country) or bypass:
            # changes the objects in each simulation
            self.simulationOne.setLocation(country)
            self.simulationTwo.setLocation(country)
            self.simulationOne.setDisease(disease)
            self.simulationTwo.setDisease(disease)

            # updates the titles of the graphs
            if disease:
                self.simMainLabel.set(disease.name)
            else:
                self.simMainLabel.set("[None]")
            if country:
                self.simLabelOne.set(country.name)
            else:
                self.simLabelOne.set("[None]")

            self.resetSim()

    def varsChanged(self, newdisease, newcountry):
        # returns true if any object does not match the currently selected object
        if newdisease != self.simulationOne.disease:
            return True
        if newcountry != self.simulationOne.country:
            return True

        return False


class SingleSimulationPage(SimulationPage):

    def __init__(self, parent, app):
        super().__init__(parent, app)      # initializes the parent class

        self.titleframe = ttk.Frame(self)
        ttk.Label(self.titleframe, text="Simulating", font=("Verdana", 21)).grid(row=0, column=0, padx=5)
        ttk.Label(self.titleframe, textvar=self.simMainLabel, font=("Verdana", 21, "bold")).grid(row=0, column=1)
        diseaseedit = ttk.Label(self.titleframe, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        diseaseedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=False: self.editVar(num=i, loc=loc))
        diseaseedit.grid(row=0, column=2, sticky="s", padx=4, pady=5)

        ttk.Label(self.titleframe, text="in", font=("Verdana", 21)).grid(row=0, column=3, padx=5)
        ttk.Label(self.titleframe, textvar=self.simLabelOne, font=("Verdana", 21, "bold")).grid(row=0, column=4)
        countryedit = ttk.Label(self.titleframe, text="edit", font=("Verdana", 10, "underline"), cursor="hand2")
        countryedit.bind("<ButtonRelease-1>", lambda e, i=1, loc=True: self.editVar(num=i, loc=loc))
        countryedit.grid(row=0, column=5, sticky="s", padx=4, pady=5)
        self.titleframe.pack()

        self.tabControl.pack(padx=3, pady=2, expand=1, fill="both")

    def simulationTab_init(self, tab):
        # overrides the normal simulation tab to display only one graph
        pagecanvas = []
        graph_frame = ttk.Frame(tab)
        graphOne = sim.DrawableCanvas(graph_frame, self.figureOne, (7, 5))
        graphOne.getCanvas().grid(row=0, column=0)
        pagecanvas.append(graphOne)
        self.canvasList.append(pagecanvas)
        graph_frame.grid(row=0, column=0, pady=8, sticky="w")

        ctrl_frame = ttk.Frame(graph_frame)

        self.playPauseFrame(ctrl_frame).pack()

        self.resetLink = ttk.Label(ctrl_frame, text="Reset", font=("Calibri", 10, "underline"), cursor="hand2")
        self.resetLink.bind("<ButtonRelease-1>", self.resetSim)
        self.resetLink.pack(pady=5)

        ttk.Label(ctrl_frame, text="Sim Speed:", font=gb.SMLFONT).pack()
        speedslider = ttk.Scale(ctrl_frame, variable=self.speedvalue, orient="horizontal", from_=0.5, to=9.9, length=120)    # when logged gives values between 0.005s and 1.3s
        speedslider.pack()

        self.checkButtonFrame(ctrl_frame).pack(anchor="n")
        self.simSettingsFrame(ctrl_frame)

        ctrl_frame.grid(row=0, column=1, sticky="n", pady=5)

    def simplifiedTab_init(self, tab):
        # overrides the normal simplified tab to display only one graph
        pagecanvas = []
        graph_frame = ttk.Frame(tab)
        graphOne = sim.DrawableCanvas(graph_frame, self.figureOne, (9.8, 4.9))
        graphOne.getCanvas().grid(row=1, column=0, columnspan=2)
        pagecanvas.append(graphOne)
        self.canvasList.append(pagecanvas)
        graph_frame.pack(pady=3, anchor="w")

        lowerframe = ttk.Frame(tab)
        lowerframe.pack(padx=36, anchor="n", fill="both")

        self.playPauseFrame(lowerframe).grid(row=0, column=0)

        self.checkButtonFrame(lowerframe, horizontal=True).grid(row=0, column=3, padx=30)

        speedslider = ttk.Scale(lowerframe, variable=self.speedvalue, orient="horizontal", from_=0.5, to=9.9, length=180)    # when logged gives values between 0.005s and 1.3s
        speedslider.grid(row=0, column=1, padx=50)

    def advancedTab_init(self, tab):
        # overrides the normal advanced tab to display only one graph
        pagecanvas = []
        graph_frame = ttk.Frame(tab)
        graphOne = sim.DrawableCanvas(graph_frame, self.figureOne, (7, 5))
        graphOne.getCanvas().grid(row=0, column=0)
        pagecanvas.append(graphOne)
        self.canvasList.append(pagecanvas)
        graph_frame.grid(row=0, column=0, pady=8, rowspan=2)

        ctrl_frame = ttk.Frame(tab)

        self.playPauseFrame(ctrl_frame).pack()

        self.resetLink = ttk.Label(ctrl_frame, text="Reset", font=("Calibri", 10, "underline"), cursor="hand2")
        self.resetLink.bind("<ButtonRelease-1>", self.resetSim)
        self.resetLink.pack(pady=5)

        ttk.Label(ctrl_frame, text="Sim Speed:", font=gb.SMLFONT).pack()
        speedslider = ttk.Scale(ctrl_frame, variable=self.speedvalue, orient="horizontal", from_=0.5, to=9.9, length=120)    # when logged gives values between 0.005s and 1.3s
        speedslider.pack()

        self.checkButtonFrame(ctrl_frame).pack(anchor="w")

        ctrl_frame.grid(row=0, column=1, padx=10)

        info_frame1 = ttk.Frame(tab)
        ttk.Label(info_frame1, text="New Cases:", font=("Verdana", 14)).grid(row=0, column=0, sticky="e")
        ttk.Label(info_frame1, text="Current Inf:", font=("Verdana", 14)).grid(row=1, column=0, sticky="e")
        ttk.Label(info_frame1, text="All Time Inf:", font=("Verdana", 14)).grid(row=2, column=0, sticky="e")
        ttk.Label(info_frame1, text="Recovered:", font=("Verdana", 14)).grid(row=3, column=0, sticky="e")
        ttk.Label(info_frame1, text="Deaths:", font=("Verdana", 14)).grid(row=4, column=0, sticky="e")
        self.adv_newcases_1 = tk.StringVar()
        self.adv_current_1 = tk.StringVar()
        self.adv_alltime_1 = tk.StringVar()
        self.adv_recovered_1 = tk.StringVar()
        self.adv_deaths_1 = tk.StringVar()
        ttk.Label(info_frame1, textvar=self.adv_newcases_1, font=("Verdana", 14)).grid(row=0, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_current_1, font=("Verdana", 14)).grid(row=1, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_alltime_1, font=("Verdana", 14)).grid(row=2, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_recovered_1, font=("Verdana", 14)).grid(row=3, column=1, sticky="w")
        ttk.Label(info_frame1, textvar=self.adv_deaths_1, font=("Verdana", 14)).grid(row=4, column=1, sticky="w")
        info_frame1.grid(row=1, column=1)

        self.updateAdvanced()

    def simSettingsFrame(self, frame):
        # overrides the preventative measures layout to fit with the single graph
        simframe = ttk.Frame(frame)

        ttk.Label(simframe, text="Preventative Measures:", font=gb.MEDFONT).grid(row=0, column=0, columnspan=4, pady=10)

        self.usevacc = tk.BooleanVar()
        self.usevacc.trace("w", self.updateVacc)
        self.vaccbutt = ttk.Checkbutton(simframe, text="Activate Vaccinations", variable=self.usevacc)
        self.vaccbutt.grid(row=1, column=0, columnspan=2)
        ttk.Label(simframe, text="Vaccination Percent:", font=gb.MEDFONT).grid(row=2, column=0, columnspan=2)
        self.vaccper = tk.DoubleVar()
        self.vaccper.trace("w", self.updateVacc)
        self.vaccscale = ttk.Scale(simframe, variable=self.vaccper, orient="horizontal", from_=0, to=1, length=80, state="disabled")
        self.vaccscale.grid(row=3, column=0, sticky="e")
        self.vacclab = tk.StringVar(value="0.0%")
        ttk.Label(simframe, textvar=self.vacclab, font=gb.MEDFONT).grid(row=3, column=1, sticky="w")
        self.updateVacc()

        self.usequar = tk.BooleanVar()
        self.usequar.trace("w", self.updateQuar)
        self.quarbutt = ttk.Checkbutton(simframe, text="Activate Quarantine", variable=self.usequar)
        self.quarbutt.grid(row=4, column=0, padx=80, columnspan=2)
        ttk.Label(simframe, text="Quarantining Level:", font=gb.MEDFONT).grid(row=5, column=0, columnspan=2)
        self.quarlvl = tk.DoubleVar(value=.5)
        self.quarlvl.trace("w", self.updateQuar)
        self.quarscale = ttk.Scale(simframe, variable=self.quarlvl, orient="horizontal", from_=.1, to=.6, length=80, state="disabled")
        self.quarscale.grid(row=6, column=0, columnspan=2)
        self.updateQuar()

        self.uselock = tk.BooleanVar()
        self.uselock.trace("w", self.updateLock)
        self.lockbutt = ttk.Checkbutton(simframe, text="Use Lockdowns", variable=self.uselock)
        self.lockbutt.grid(row=7, column=0, columnspan=2)
        ttk.Label(simframe, text="Lockdown Intensity:", font=gb.MEDFONT).grid(row=8, column=0, columnspan=2)
        self.locklvl = tk.DoubleVar(value=.1)
        self.locklvl.trace("w", self.updateLock)
        self.lockscale = ttk.Scale(simframe, variable=self.locklvl, orient="horizontal", from_=.6, to=0, length=80, state="disabled")
        self.lockscale.grid(row=9, column=0, columnspan=2)
        self.updateLock()

        simframe.pack(pady=5)

    def updateVars(self, *a, bypass=False):
        # updates the simulation varaibles if they have changed
        disease = gb.simDisease1
        country = gb.simLocation1

        if self.varsChanged(disease, country) or bypass:
            # changes the objects in the simulation
            self.simulationOne.setLocation(country)
            self.simulationOne.setDisease(disease)

            # updates the titles of the graph
            if disease:
                self.simMainLabel.set(disease.name)
            else:
                self.simMainLabel.set("[None]")
            if country:
                self.simLabelOne.set(country.name)
            else:
                self.simLabelOne.set("[None]")

            self.resetSim()

    def varsChanged(self, newdisease, newcountry):
        # returns true if any object does not match the currently selected object
        if newdisease != self.simulationOne.disease:
            return True
        if newcountry != self.simulationOne.country:
            return True

        return False

    def playPauseButton(self, *a):
        # overrides the normal play pause function to only check for one valid simulation object
        if self.simulationOne.runnable:     # only runs when the simulation can be started
            if self.simRunning:               # if the simulation is already running
                self.simRunning = False       # the simulation is stopped
                self.playlabel.set("▶")       # and the button is set to a play symbol
            else:                             # if the simulation is not running
                self.simRunning = True        # the simulation is started
                self.playlabel.set("⏸")      # and the button is set to a pause symbol

                interval = 1 - log(self.speedvalue.get(), 10)    # the time interval between each step in the simulation calculated with the slider
                simthread = threading.Thread(target=lambda: self.runSimulation(interval=interval))      # a thread is created, running the simulation
                simthread.daemon = True        # set to daemon, so if the main program stops running, the thread will be killed
                simthread.start()              # the thread is started

    def nextTimestep(self, button=False, *a):
        # overrides the normal next timestep function to only call the next timestep of one simulation
        # button=True when the next timestep button is clicked which can only pass if the simulation is not running
        if self.simRunning != button:             # (sim running) XOR (next button clicked); allows next timestep to be calculated if only one is true
            self.currentTime += 1               # sim timestep is updated
            self.figureOne.nextTimestep()       # next timestep calculated for first sim
            self.drawGraphs()                   # both graphs are updated

    def updateAdvanced(self):
        # overrides the normal function to only display advanced info for one simulation
        t = self.currentTime
        self.adv_newcases_1.set(self.figureOne.simulation.newplot[t])
        self.adv_current_1.set(self.figureOne.simulation.infplot[t])
        self.adv_alltime_1.set(sum(self.figureOne.simulation.newplot[:t+1])+self.figureOne.simulation.infplot[0])
        self.adv_recovered_1.set(self.figureOne.simulation.recplot[t])
        self.adv_deaths_1.set(self.figureOne.simulation.morplot[t])


class StartingScreen(ttk.Frame):
    # screen that is displayed while other pages below it are initialized

    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        self.app = app

        tk.Label(self, text="starting . . .", font=("Verdana", 16)).place(relx=0.5, rely=0.5, anchor="s")


class ClosingScreen(ttk.Frame):
    # screen that is displayed while other pages below it are destroyed

    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        self.app = app

        tk.Label(self, text="closing . . .", font=("Verdana", 16)).place(relx=0.5, rely=0.5, anchor="s")


if __name__ == "__main__":
    PandemicApp = App()
    PandemicApp.protocol("WM_DELETE_WINDOW", PandemicApp.close)    # assigns a function to run when the window is closed
    PandemicApp.mainloop()
