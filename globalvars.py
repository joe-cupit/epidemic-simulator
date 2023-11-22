# APPLICATION VARIABLES
WIDTH, HEIGHT = 1000, 600
bgcol = "white"


# FONTS
TITLEFONT = ("Arial", 26)
SUBFONT = ("Verdana", 23, "bold")
BIGFONT = ("Verdana", 14)
MIDFONT = ("Verdana", 13)
MEDFONT = ("Verdana", 11)
MEDIFONT = ("Verdana", 11, "italic")
MEDBFONT = ("Verdana", 11, "bold")
SMLFONT = ("Verdana", 9)


# DISEASE AND COUNTRY OBJECTS
class Country:

    def __init__(self, data):
        self.data = data               # stores the whole csv row
        self.name = data[0]            # the name of the country/location
        if data[1] == "Null":          # null means there are no colours on the world map associated with this loaction
            self.colours = []          # so the colours are set as empty
        else:
            self.colours = data[1].split("|")         # the colours are split to allow for multiple colours to represent the same object
        self.continent = data[2]                      # stores the continent name of the location - set to "custom" for custom locs
        self.pop = int(data[3])                       # stores the population of the location
        self.area = int(data[4])                      # stores the area of the location in km^2
        self.density = round(self.pop/self.area, 1)   # stores the density rounded to 1 decimal place


class Disease():

    def __init__(self, data):
        self.id = None
        self.name = data[0]               # disease name
        self.r0 = float(data[1])          # r0 value of the disease
        self.drate = float(data[2])       # mortality rate as a decimal (1 = 100%)
        self.makepercent()                # stores the mortality rate as a percentage
        self.incubation = int(data[3])
        self.infectious = int(data[4])
        self.respiritory = int(data[5])   # Boolean value for if the disease affects respiritory
        self.custom = int(data[6])        # Boolean value stating if the disease is user defined
        self.about = data[7]              # stores the about paragraph
        self.history = data[8]            # stores the history paragraph

    def makepercent(self):
        self.dpercent = str(round(self.drate*100, 4)) + "%"


# SIMULATION PARAMETERS
simEditing = 1           # 1 edits the first, 2 edits the second variable
simLocation1 = None
simLocation2 = None
simDisease1 = None
simDisease2 = None

simCapacity = 50000      # limits the number of individuals simulated

return_frame = None      # stores the frame to return to when going back
