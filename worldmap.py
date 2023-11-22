import globalvars as gb

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import csv


# simplified version of 'App' class in 'main.py' only used when this file is ran by itself
class baseApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        self.config(bg="white")
        self.resizable(False, False)

        self.currentPage = WorldMapPage

        container.pack(side="top", fill="both", expand=True)

        self.title("World Map")
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}
        frame = WorldMapPage(container, self)
        self.frames[WorldMapPage] = frame
        frame.pack(fill="both", expand=True)

        self.showPage(WorldMapPage)

    def showPage(self, cont):
        gb.return_frame = self.currentPage
        frame = self.frames[cont]
        self.currentPage = cont
        frame.tkraise()


class WorldMapPage(ttk.Frame):

    def __init__(self, parent, app):
        global bg_image                    # bg_image must be global so image can be clickable
        ttk.Frame.__init__(self, parent)   # initializes the parent class
        self.app = app                     # the base app class

        self.country = tk.StringVar()                           # string variable to display the country name that the user is hovered over
        self.country.trace("w", self.updateComboOptions)        # everytime the variable is written to, the trace function is called

        self.canvas = tk.Canvas(self, width=gb.WIDTH, height=gb.HEIGHT, bg="white", highlightthickness=0)  # creates a canvas for the image to be displayed
        self.canvas.pack(fill="both", expand=True)                                                         # fills the screen with the canvas

        bg_image = ImageTk.PhotoImage(map_image)        # loads the PIL image as a tkinter photo image

        self.canvas.create_image(0, 0, image=bg_image, anchor="nw")     # adds the photo image to the canvas

        self.optn = ttk.Combobox(self, textvar=self.country, font=gb.MEDFONT)    # creates a tkinter combobox, setting the variable to the current country
        self.optn.bind("<<ComboboxSelected>>", self.clickComboBox)               # runs every time an item is selected from the list
        self.optn.bind("<Return>", self.enterComboBox)                           # runs every time the enter button is clicked from within the entry
        self.optn["values"] = country_li                                         # stores a list of only country names for use in the selection
        self.canvas.create_window(540, 40, window=self.optn)

        self.customCountryFrame()    # adds the custom country frame to the canvas

        self.canvas.bind("<ButtonRelease-1>", self.clickedCountry)       # runs every time the user clicks the map
        self.canvas.bind("<Motion>", self.movedMouse)                  # runs every time the user moves the mouse over the map

        tk.Button(self, text="🡰", width=6, command=self.back).place(x=10, y=10)

    def customCountryFrame(self):
        fr = ttk.Frame(self)
        for i in range(5):                    # loops through the 5 custom locations
            country = customlocationlist[i]   # gets the object for the custom location
            add = tk.Button(fr, text="+", font=gb.MEDFONT, width=2, cursor="hand2",    # creats a '+' button for the custom loc
                            command=lambda i=i: self.addCustom(i))
            add.grid(row=i, column=1)
            new = tk.Button(fr, text=country.name, font=gb.MEDFONT, width=14, cursor="hand2",   # creats a button that can edit the custom loc
                            command=lambda i=i: self.editCustom(i))
            new.grid(row=i, column=0)
            if len(country.colours) == 0:      # if there is no custom location currently
                add["state"] = "disabled"      # the add button is disabled
                new["font"] = gb.MEDIFONT      # the font of name button is made itallic
        self.canvas.create_window(25, 420, window=fr, anchor="nw")        # the buttons are placed on the canvas

    def addCustom(self, index):
        c = customlocationlist[index]        # gets the custom location object for the index of button clicked
        addToSimulation(c)                   # adds the object to the simulation
        self.app.showPage(gb.return_frame)   # returns to the previous frame

    def editCustom(self, index):
        c = customlocationlist[index]       # gets the custom location object for the index of button clicked
        self.showCountryPopup(c, custom=True)      # opens a popup for that custom location that the user can edit with

    def enterComboBox(self, event):
        self.updateComboOptions()                 # makes sure the results shown are limited to starting with what is entered
        self.optn.event_generate('<Button-1>')    # opens the combobox list

    def clickComboBox(self, *args):
        # whenever a country on the list is clicked
        country = namecountrydict[self.country.get()]        # its object its retried using its name as the key
        self.country.set("")                                 # the name showing in the box is reset to an empty string
        self.showCountryPopup(country)                              # the popup related to the country object is shown

    def updateComboOptions(self, *args):
        limit = self.country.get().lower()                                # gets the text currently in the entry box
        new = [c for c in country_li if c.lower().startswith(limit)]      # forms a new list consisting only of countries starting with the text in the entry
        self.optn['values'] = new                                         # the options related to the combobox are set to the new

    def getCountryObject(self, pos):
        nameid = '%02x%02x%02x' % map_image.getpixel((pos.x, pos.y))   # gets the hex code for the current pixel
        try:
            return hexcountrydict[nameid.upper()]         # if the colour exists in the dictionary the country name related is returned
        except KeyError:
            return ""                                     # otherwise an empty string is returned

    def movedMouse(self, pos):
        if curr := self.getCountryObject(pos):            # when there is a country below the mouse..
            self.config(cursor="hand2")              # ..the cursor is changed to a selection cursor
            self.country.set(curr.name)              # ..the country name at the top of the window is updated
        else:
            self.config(cursor="")                   # otherwise the cursor is set back to deafult
            if self.country.get() in country_li:     # and if there is a country being displayed at the top of the window
                self.country.set("")                 # it is reset to an empty string
        self.app.update_idletasks()

    def clickedCountry(self, pos):
        if country := self.getCountryObject(pos):      # only tries to open a pop-up if there is a country under the mouse
            self.showCountryPopup(country)

    def showCountryPopup(self, country, custom=False):
        try:
            self.countrypopup.destroy()      # if there is already a country pop-up, it will be destroyed before the new one is created
        except AttributeError:
            pass

        self.countrypopup = tk.Toplevel(self.master)                    # creates a new base window to create the country pop-up
        if custom:
            CustomLocationPage(self, self.countrypopup, country)        # creates a different page for custom locationns
        else:
            CountryPage(self, self.countrypopup, country)

    def back(self):
        self.app.showPage(gb.return_frame)


class CountryPage():

    def __init__(self, master, top, country):
        self.master = master                 # world map page
        self.top = top                       # popup window
        tmpx, tmpy = self.master.app.winfo_x(), self.master.app.winfo_y()   # finds the current position of the window
        self.top.geometry(f"200x320+{tmpx+130}+{tmpy+100}")                 # places the new window in a set place relative to the main window position
        self.top.resizable(False, False)         # makes the popup non resizable
        self.frame = tk.Frame(self.top)          # base frame for widgets on the popup
        self.frame.pack()
        self.country = country           # stores the country popup of the popup

        self.layoutInit()                # initializes the popup layout

    def layoutInit(self):
        self.top.title(self.country.name)           # sets the name of the window to the country name

        # places widgets on the frame
        tk.Label(self.frame, text=self.country.name, font=gb.MEDFONT).pack()
        tk.Label(self.frame, text=self.country.continent).pack()
        labelframe = tk.Frame(self.frame)
        labelframe.pack(pady=5)
        tk.Label(labelframe, text="Pop:").grid(row=0, column=0, sticky="e")
        tk.Label(labelframe, text="Area:").grid(row=1, column=0, sticky="e")
        tk.Label(labelframe, text="Density:").grid(row=2, column=0, sticky="e")
        po = tk.Label(labelframe, text="{:,}".format(self.country.pop))
        po.grid(row=0, column=1, sticky="w")
        area = "{:,}".format(int(self.country.area)), "Km²"
        ar = tk.Label(labelframe, text=area)
        ar.grid(row=1, column=1, sticky="w")
        dens = "{:,}".format(self.country.density), "P/Km²"
        de = tk.Label(labelframe, text=dens)
        de.grid(row=2, column=1, sticky="w")

        ttk.Button(self.frame, text="Add to Sim", command=self.add).pack(pady=5)
        ttk.Button(self.frame, text="Close", command=self.top.destroy, width=7).pack()

        # a warning is added if the population is more than the set simulation capacity
        if self.country.pop > gb.simCapacity:
            tk.Message(self.frame, text=(f"A simulation of {gb.simCapacity} members will be used. \nThis can be changed in the settings."), fg="red", justify="center", width=180).pack(pady=15)

    def add(self):
        addToSimulation(self.country)                # adds the country object to the global variables file
        self.top.destroy()                           # destorys the page
        self.master.app.showPage(gb.return_frame)    # shows the previous frame (usually a simulation page)


class CustomLocationPage(CountryPage):
    # inherits from country page to allow for same basic layout

    def layoutInit(self):
        self.num = int(self.country.continent)     # the custom country's position in the list
        self.top.title("Custom Slot")
        self.customname = tk.StringVar()           # stores the name the user enters for the location
        self.customname.set(self.country.name)     # originally sets the name to the current object name
        self.popu = tk.StringVar()                 # stores the population the user enters
        self.popu.set(self.country.pop)
        self.area = tk.StringVar()                 # stores the area the user enters
        self.area.set(self.country.area)
        self.dens = tk.StringVar()                 # stores the density the user enters
        self.dens.set(self.country.density)

        # user entry section
        ttk.Entry(self.frame, textvar=self.customname, font=gb.MEDFONT,       # the entry for the location name
                  justify="center", width=14).pack(pady=8)

        labelframe = tk.Frame(self.frame)
        labelframe.pack(pady=5)
        tk.Label(labelframe, text="Pop:").grid(row=0, column=0, sticky="e")
        tk.Label(labelframe, text="Area:").grid(row=1, column=0, sticky="e")
        tk.Label(labelframe, text="Density:").grid(row=2, column=0, sticky="e")

        p = ttk.Entry(labelframe, textvar=self.popu, width=8)                # entry for population
        p.grid(row=0, column=1, sticky="w")
        a = ttk.Entry(labelframe, textvar=self.area, width=8)                # entry for area
        a.grid(row=1, column=1, sticky="w")
        tk.Label(labelframe, text="Km²").grid(row=1, column=2, sticky="w")
        d = ttk.Entry(labelframe, textvar=self.dens, width=8)                # entry for density
        d.grid(row=2, column=1, sticky="w")
        tk.Label(labelframe, text="P/Km²").grid(row=2, column=2, sticky="w")

        # buttons
        add = ttk.Button(self.frame, text="Add to Sim", command=self.addcustom)
        add.pack(pady=5)
        ttk.Button(self.frame, text="Save", command=self.savecustom, width=7).pack()
        ttk.Button(self.frame, text="Reset", command=self.resetcustom, width=7).pack()
        ttk.Button(self.frame, text="Close", command=self.top.destroy, width=7).pack()

    def savecustom(self, status="Full"):
        i = self.num-1                      # gets the index of the custom location
        # creates a new list of data for the country class and edits the location object variables
        newrow = [self.customname.get(), status, str(i+1), self.popu.get(), self.area.get(), self.dens.get()]
        self.country.name = newrow[0]
        self.country.colours = newrow[1]
        self.country.pop = int(newrow[3])
        self.country.area = int(newrow[4])
        self.country.density = float(newrow[5])

        self.savetocsv(newrow, i)           # saves the list of data to customlocs.csv at the index of the country

    def resetcustom(self):
        # sets the variables of the country object back to the deafult values
        self.customname.set("Empty Slot")
        self.popu.set(1)
        self.area.set(1)
        self.dens.set(1.0)

        # saves the new variables
        self.savecustom(status="Null")

    def savetocsv(self, row, num):
        # opens the csv file and saves the rows
        with open("customlocs.csv", "r") as f:
            rows = list(csv.reader(f, delimiter=','))
        # changes the row for the changed object to the new information
        rows[num] = row
        # opens the csv in write mode and writes the edited rows to it
        with open("customlocs.csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(rows)
        # changes the object in the custom loc list
        customlocationlist[num] = gb.Country(row)
        # updates the custom country frame on the world map page
        self.master.customCountryFrame()

    def addcustom(self):
        # saves the object then adds it to the simulation
        self.savecustom()
        self.add()


def createCountryDict():
    hexcountrydict = {}        # a dictionary linking hex colours to country objects - hexcountrydict[HEX] = country object
    namecountrydict = {}       # a dictionary linking a country name to country objects - namecountrydict[Name] = country object

    with open("countries.csv", "r") as f:     # opens the csv storing country names and related information
        reader = csv.reader(f, delimiter=',')
        for row in reader:                          # loops through every country in the csv
            c = gb.Country(row)                     # creates a country object with the information stored in the row
            if row[1] != "Null":                    # if there is a colour related to the country..
                for col in row[1].split("|"):       # ..all its related colours are looped through..
                    hexcountrydict[col] = c         # ..and each colour is set as a key pointing to the country object
            namecountrydict[row[0]] = c             # the name is set as a key for the country object

    customlocationlist = []                         # list storing all custom location objects
    with open("customlocs.csv", "r") as f:          # opens the custom location csv file
        reader = csv.reader(f, delimiter=',')
        for row in reader:                          # loops through every custom location
            c = gb.Country(row)                     # creates a country object with the information stored in the row
            customlocationlist.append(c)            # appends the country object to the custom location list
            namecountrydict[c.name] = c             # adds the custom location to the name dictionary

    return hexcountrydict, namecountrydict, customlocationlist


def addToSimulation(country_object):
    # given a country object, it is assigned to the correct global variable based on which location is being edited
    if gb.simEditing == 1:
        gb.simLocation1 = country_object
    elif gb.simEditing == 2:
        gb.simLocation2 = country_object
    else:
        print("Error adding to simulation: Simulation is not currently editing a location variable")


map_image = Image.open("worldmap.png")           # loads the background image
bg_image = 0                                     # defines bg_image in the global scope
hexcountrydict, namecountrydict, customlocationlist = createCountryDict()     # saves the country objects
country_li = list(namecountrydict.keys())        # creates a list of country names


if __name__ == "__main__":
    # allows the 'worldmap.py' file to be ran by itself for easy testing of world map
    tkapp = baseApp()
    tkapp.geometry(str(gb.WIDTH)+"x"+str(gb.HEIGHT))
    tkapp.mainloop()
