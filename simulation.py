import globalvars as gb   # global variables

import matplotlib.pyplot as plt           # plots/creates matplotlib graphs
from matplotlib.figure import Figure      # creates matplotlib figures
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg   # allows matplotlib figures on tkinter gui

import numpy as np
import math


class Individual:

    def __init__(self, mean_infection_len):
        self.mean_infection_len = mean_infection_len       # stores the mean infection length for the current disease

    def infect(self, timestep):
        self.infectedat = timestep             # infects the infividual by saving the timestep of infection

    def getInfectionLen(self, timestep):
        return (timestep-self.infectedat)      # returns the number of timesteps the infividual has been infected

    def calcRecovery(self, timestep, recovery_dict):
        infectcur = self.getInfectionLen(timestep) - self.mean_infection_len    # works out the individuals length of infection relative to mean length
        try:
            return recovery_dict[infectcur]    # returns the chance of recovrey using lookup dictionary
        except KeyError:
            if infectcur > 10:                 # if the relative infection len is not in the dictionary
                return 1                       # and the infection len is more than 10 past the mean, a chance of 1 is returned
            return 0                           # otherwise a chance of 0 is returned


class Simulation:

    def __init__(self, country, disease):
        self.country = country      # stores the simulation location
        self.disease = disease      # stores the simulation disease
        self.startinf = 10          # stores the number of individuals given the disease at the start of sim
        self.recovery_dict = self.generateRecoveryChances()    # dictionary lookup of cumulative Normal for recovery chances

        self.vaccinated_perc = 0          # percentage of vaccinated individuals

        self.usequarantine = False        # boolean if user selected quarantine for sim
        self.quarantine_lvl = 0.5         # stores the level of quarantine (how intense it is enforeced)

        self.uselockdown = False          # boolean if user selected lockdown use for sim
        self.lockdown = False             # boolean if sim is currently in lockdown
        self.lockdown_intensity = .1     # float that stores the proportion of infected needed to start lockdown

        self.resetSim()             # resets simulation

    def resetSim(self):
        if self.country and self.disease:    # if the simulation has a country and disease object
            self.runnable = True             # the simulation is set as runnable so can be played
            self.simInit()                   # the simulation is initialised
        else:                                # otherwise
            self.runnable = False            # the simulation is set as not runnable so cannot be played
            self.emptySimInit()              # an empty simulation is initialised so it works with the simulation figure

    def simInit(self):
        self.timestep = 0
        if self.country.pop > gb.simCapacity:                                         # if the country population is over the set sim capacity
            self.individuals = gb.simCapacity                                         # the simulation individuals is set to the capacity
            self.gridwidth = int(math.sqrt(gb.simCapacity / self.country.density))    # the gridwidth is adjusted to match the country density
        else:
            self.individuals = self.country.pop                                       # otherwise the individuals is kept the same
            self.gridwidth = int(math.sqrt(self.country.area))                        # and the grid width is set to match the country area

        self.grid = self.emptySimulationGrid()           # grid is initialised to an empty 2d numpy array
        ips = self.individuals // (self.gridwidth**2)    # ips = Individual Per Square
        for row in range(self.gridwidth):
            for col in range(self.gridwidth):            # loops through every location on the grid
                for i in range(ips):                     # appends correct amount of individual objects to the locations
                    self.grid[row][col][0].append(Individual(self.disease.infectious))
        for i in range(self.startinf):                   # loops through the amount of starting infected
            r = np.random.randint(0, self.gridwidth)     # chooses a random row and column
            c = np.random.randint(0, self.gridwidth)
            indiv = self.grid[r][c][0].pop(0)            # removes 1 individual from the locatoin
            indiv.infect(0)                              # infects the individual
            self.grid[r][c][1].append(indiv)             # appends the indivual to the locations infected list

        self.susplot = [ips*(self.gridwidth**2) - self.startinf]   # starting susceptible is total individuals - starting infected
        self.infplot = [self.startinf]                             # starting infected set
        self.recplot = [0]                                         # starting recovered set
        self.morplot = [0]                                         # starting mortalities set
        self.newplot = [0]                                         # starting new cases set

    def emptySimInit(self):
        # initialises an empty simulation that works with a simulation figure object
        self.susplot = [0]
        self.infplot = [0]
        self.recplot = [0]
        self.morplot = [0]
        self.newplot = [0]

    def generateRecoveryChances(self):
        recovery_dict = {}         # dictionary to store probabilities
        cumulative = 0             # stores cumulative probablities
        for i in range(-10, 10):                  # loops through 10 days before and after average infection len
            p = math.exp(-((i**2)/2))/math.sqrt(2 * math.pi)      # Normal dist; mean 0, variance 1; at n=i
            cumulative += p                       # stores cumulative
            recovery_dict[i] = cumulative         # assigns prob to dictionary at day number (i)
        return recovery_dict

    def emptySimulationGrid(self):
        emptygrid = np.empty((self.gridwidth, self.gridwidth, 4), dtype=object)   # creates a 3d numpy array of empty objects
        for i in np.ndindex(emptygrid.shape):   # the array is looped through
            emptygrid[i] = []                   # each location is set to an empty list
        return emptygrid                        # the array is returned

    def get_new_loc(self, r, c, movechance=0.8):
        pos = [r, c]                              # current position stored
        if np.random.uniform(0, 1) < movechance:  # randomly decided if individual moves
            lim = self.gridwidth                  # stores the width of the grid as the limit of movement
            dire = np.random.randint(0, 2)        # the axis the individual moves is randomly chosen

            mean = (lim / 2) - pos[dire]          # mean is half the grid width take away the current position (individuals travel towards centre)
            dist = np.random.normal(mean, 100)    # distance travelled decided with Normal distribution with standard deviation 100
            new = dist + pos[dire]                # new location is calculated
            if new >= lim or new <= 0:            # if the new loc is outside limit of grid
                dist = mean                       # the distance is set to the calculated mean

            pos[dire] += int(dist)                # the travelled distance is added to the pos of the decided axis

        return pos[0], pos[1]                     # the new position is returned

    def nextTimestep(self):
        self.timestep += 1        # increases timestep by 1
        gridtot = [0, 0, 0, 0]    # create a list to store data for the graph  [susceptible, infected, recovered, mortalities]
        newcases = 0              # variable used to keep track of new cases for the timestep

        for row in range(self.gridwidth):
            for col in range(self.gridwidth):
                loc = list(self.grid[row][col])       # creates a copy of the current location
                newloc = list(loc)                    # creates a copy that can be edited

                newloc, new = self.infectGridLoc(loc, newloc)   # infects individuals
                newloc = self.recoverGridLoc(loc, newloc)       # recovers individuals

                gridtot[0] += len(newloc[0])           # adds current susceptible to the counting total
                gridtot[1] += len(newloc[1])           # adds current infected
                gridtot[2] += len(newloc[2])           # adds current recovered
                gridtot[3] += len(newloc[3])           # adds current mortalities
                newcases += new                        # adds current newcases to counting total
                self.grid[row][col] = list(newloc)     # updates the location on the grid

        newgrid = self.moveIndividuals(self.grid)       # moves all individuals on the grid
        self.grid = np.copy(newgrid)                   # updates the grid with moved individuals

        if self.uselockdown:                  # if the user has activated lockdown for the simulation
            self.checkLockdown(gridtot)       # it is checked if the simulation should enter or end a lockdown

        self.susplot.append(gridtot[0])       # appends this timestep susceptible to the list of susceptible values
        self.infplot.append(gridtot[1])       # does the same with infectious;
        self.recplot.append(gridtot[2])       # recovered,
        self.morplot.append(gridtot[3])       # mortalities,
        self.newplot.append(newcases)         # newcases

    def infectGridLoc(self, loc, newloc):
        # takes the current location on the grid, and the newloc to return the newloc with infected individuals
        # base infection chance for each susceptible person if there is one infected individual
        inf_chance = 0.00004 * self.disease.r0 * (1 - self.vaccinated_perc**2)
        if self.lockdown:
            inf_chance = inf_chance / 10    # if simulation is currently in lockdown the infected chance is reduced

        newcases = 0          # stores new cases for this location
        for indiv in loc[0]:                    # loops through all susceptible individuals
            # chance of getting infected increased based on number of infected on the location
            if np.random.uniform(0, 1) < inf_chance * len(loc[1]):
                newloc[0].remove(indiv)         # idividual removed from susceptible list
                indiv.infect(self.timestep)     # the individual is infected
                newloc[1].append(indiv)         # added to infected list
                newcases += 1                   # new cases increased

        return newloc, newcases

    def recoverGridLoc(self, loc, newloc):
        # takes the current location on the grid, and the newloc to return the newloc with recovered individuals
        for indiv in loc[1]:                                                                             # loops through all infected individuals
            if self.usequarantine and np.random.uniform(0, 1) < self.quarantine_lvl:                     # if quarantine active, user is quarantined based on random number
                newloc[1].remove(indiv)        # removed from infected list
                newloc[2].append(indiv)        # added to deaths list
            elif np.random.uniform(0, 1) < indiv.calcRecovery(self.timestep, self.recovery_dict):        # users recovery chance is calculated and compared to random number
                newloc[1].remove(indiv)        # removed from infected list
                if np.random.uniform(0, 1) < self.disease.drate * (1 - (self.vaccinated_perc / 2)):      # chance of the user being moved to deaths instead of recovering is calculated
                    newloc[3].append(indiv)    # added to deaths list
                else:
                    newloc[2].append(indiv)    # added to recovered list
        return newloc

    def moveIndividuals(self, grid):
        # takes in grid in the form of numpy array and returns new grid with moved individuals
        newgrid = self.emptySimulationGrid()    # creates an empty numpy grid of the simulation grid size
        movechance = 0.8                        # sets the default move chance
        if self.lockdown:                                          # if simulation curretnly in lockdown
            movechance = movechance * self.lockdown_intensity      # the movechance is multiplies by lockdown propotion (lowering it)

        for row in range(self.gridwidth):
            for col in range(self.gridwidth):
                loc = list(self.grid[row][col])         # creates a copy of the current location

                for indiv in loc[0]:                                              # loops through all susceptible individuals
                    a, b = self.get_new_loc(row, col, movechance=movechance)      # gets individuals new location after moving
                    newgrid[a][b][0].append(indiv)                                # appends the individuals object to the new location

                for indiv in loc[1]:                                                           # loops through all infected individuals
                    if indiv.getInfectionLen(self.timestep) > self.disease.incubation:         # if the infected individual if out of the incubation period..
                        if self.usequarantine:                                                                     # if the simulation uses quarantine, the movechance is scaled..
                            a, b = self.get_new_loc(row, col, movechance=(movechance/(10*self.quarantine_lvl)))     # ..based on the quarantine level
                        else:                                                                  # if there is no quarantine..
                            a, b = self.get_new_loc(row, col, movechance=(movechance*(3/4)))   # ..the individual is moved at a reduced chance
                    else:                                                                      # if the individual is still in the incubation period..
                        a, b = self.get_new_loc(row, col, movechance=movechance)               # ..they are moved as normal
                    newgrid[a][b][1].append(indiv)                                # appends the individuals object to the new location

                newgrid[row][col][2] = list(loc[2])    # the recovered individuals and mortalites are not moved as they do not affect disease spread
                newgrid[row][col][3] = list(loc[3])    # which saves computation

        return newgrid       # the changed grid is returned

    def checkLockdown(self, gridtot):
        infected = gridtot[1]
        if self.lockdown:                                                       # if lockdown is curretly active..
            if (infected / sum(gridtot)) < (self.lockdown_intensity / 5):       # ..and if the proportion of infected people is less than 1/5 of the lockdown proportion..
                self.lockdown = False                                           # ..lockdown is ended
        else:                                                                   # if there is not curretnly lockdown..
            if (infected / sum(gridtot)) > (self.lockdown_intensity):        # ..and if the proportion of infected people is higher than the lockdown proportion..
                self.lockdown = True                                            # ..lockdown is started

    def getGraphPlots(self, timestep):
        # Returns the plots for the graph up to a given timestep
        timestep += 1                                  # timestep is increased by 1 so it gets all needed plots in the list including index 0
        plots = []
        plots.append(self.susplot[:timestep])
        plots.append(self.infplot[:timestep])
        plots.append(self.recplot[:timestep])
        plots.append(self.morplot[:timestep])
        plots.append(self.newplot[:timestep])
        return [i for i in range(timestep)], plots     # returns timesteps and plots

    def setLocation(self, country):
        # takes a disease object and stores it in simulation disease variable
        self.country = country
        self.resetSim()

    def setDisease(self, disease):
        # takes a disease object and stores it in simulation disease variable
        self.disease = disease
        self.resetSim()

    # runs the simulation when simulation.py is ran by itself
    def runSimulation(self, timesteps):
        for t in range(timesteps):
            self.nextTimestep()

    # plots the graph when the simulation.py is ran by itself
    def plotSingleGraph(self):
        xaxis = [i for i in range(self.timestep+1)]
        plt.plot(xaxis, self.infplot, label="infected")
        plt.plot(xaxis, self.morplot, label="deceased")
        plt.bar(xaxis, self.newplot, label="new cases", width=1)
        plt.xlabel("timestep")
        plt.ylabel("population")
        plt.title("disease spread")
        plt.xlim((0, self.timestep))

        print("Most new cases in a day: " + str(sorted(self.newplot)[-1]))
        print("Amount of people infected: " + str(self.individuals-self.susplot[-1]))
        print("Total deaths: " + str(self.morplot[-1]))

        plt.show()


class SimulationFigure:

    def __init__(self, ctrl, simulation):
        self.ctrl = ctrl                   # the page the figure is going on
        self.simulation = simulation       # the simulatin object of the figure

        self.loadedTimesteps = 1
        self.uselegend = True

        self.linefigure = Figure(figsize=(5, 4), dpi=100)                                                   # creates a matplotlib figure of deafult size
        self.linefigure.subplots_adjust(left=0.12, right=0.94, top=0.975, bottom=0.08, wspace=0, hspace=0)  # removes the white space around the figure

        self.figplot = self.linefigure.add_subplot(111)                        # creates a plot on the figure
        susplot, = self.figplot.plot(([0], simulation.susplot), "blue")        # plots the simulation values onto the plot
        infplot, = self.figplot.plot(([0], simulation.infplot), "red")
        recplot, = self.figplot.plot(([0], simulation.recplot), "green")
        morplot, = self.figplot.plot(([0], simulation.morplot), "black")
        newplot, = self.figplot.plot(([0], simulation.newplot), "purple")
        self.plotlist = [susplot, infplot, recplot, morplot, newplot]        # stores the plots in list for accessibility and editing
        self.plotname = ["Sus", "Inf", "Rec", "Dead", "New"]                 # stores associated names for the plots for use in legend
        self.vislist = [0, 1, 0, 0, 1]                                       # stores associated boolean values for if the plot is visible

        self.updateLegend()
        self.updateGraph()

    def getFigure(self):
        return self.linefigure        # returns the figure for use in DrawableCanvas objects

    def getMaxPoint(self):
        maxplot = 0
        for i in range(len(self.vislist)):           # loops through the range of plots
            if self.vislist[i] and max(self.values[i][:self.ctrl.currentTime+1]) > maxplot:   # if the plot is visible and its max is bigger than current max
                maxplot = max(self.values[i])                                                 # the max is set to the plot max

        if maxplot < 46:
            return 50                      # minimum y axis limit is 50
        else:
            return int(maxplot * 1.1)      # y axis max is set higher to leave room between top of the graph and figure

    def getVisiblePlots(self):
        plotli, nameli = [], []
        for i in range(len(self.plotlist)):          # loops through figure plots
            if self.vislist[i]:
                plotli.append(self.plotlist[i])      # for every plot that is visible, it is appended to the plot list
                nameli.append(self.plotname[i])      # and its name appended to the name list
        return plotli, nameli

    def updateLegend(self):
        if not self.uselegend:     # if the figure is selected to not be shown
            self.leg.remove()      # the legend is removed and the function returns
            return 0
        p, n = self.getVisiblePlots()     # gets a list of visible figure plots and a list of corresponding names for the legend
        if len(p) > 0:
            # if there is more than one visible plot, the legend is set in the top left
            self.leg = self.figplot.legend(p, n, loc="upper left", fancybox=False)

    def setVisible(self, vis):
        # takes a list of boolean values that decide visibility
        self.vislist = vis
        self.updateLegend()

    def configLimit(self, limit):
        # takes a limit for the y axis and sets the figures y axis limit to that, used for scaling graphs
        self.figplot.set_ylim(0, limit)
        self.updateGraph()
        self.updateLegend()

    def setSim(self, simulation):
        # takes a simulation object and sets the figure's simulation to that object, then resets the figure/sim
        self.simulation = simulation
        self.resetSim()

    def resetSim(self):
        self.simulation.resetSim()
        self.loadedTimesteps = 1
        self.updateGraph()

    def nextTimestep(self):
        # when the currently displayed timestep is the same or more than the amount of loaded timesteps, the next timestep must be loaded
        # if the currently displayed timestep is lower than the loaded timesteps the next timestep is not unecessarily loaded
        if len(self.values[0]) >= self.loadedTimesteps:
            self.simulation.nextTimestep()
            self.loadedTimesteps += 1

    def updateGraph(self):
        self.xplot, self.values = self.simulation.getGraphPlots(self.ctrl.currentTime)   # gets timesteps and simulation plots up to the current timestep

        if len(self.xplot) > 1:
            self.figplot.set_xlim(0, self.xplot[-1])     # sets the x limit of the graph to between 0 and current timestep
        else:
            self.figplot.set_xlim(0, 1)                  # if the current timestep is 0, the x axis is set between 0 and 1

        for i, plot in enumerate(self.plotlist):    # loops through figure plots with i storing its index in the list of plots
            values = self.values[i]                 # gets the simulation values for the current figure plot
            plot.set_data(self.xplot, values)       # plots to values to the figure
            if self.vislist[i]:
                plot.set_linestyle("-")             # if the current figure plot is selected to be visible, its linestyle is turned on
            else:
                plot.set_linestyle("none")          # otherwise its linestyle is set to none


class DrawableCanvas:

    def __init__(self, master, figure, figsize):
        # function takes the frame it will be placed, the SimulationFigure object, and the desired figure size as a list
        self.figwidth = figsize[0]
        self.figheight = figsize[1]
        self.figure = figure.getFigure()

        self.figure.set_figwidth(self.figwidth)
        self.figure.set_figheight(self.figheight)

        self.canvas = FigureCanvasTkAgg(self.figure, master=master)   # creates a tkinter canvas that can display matplotlib figures
        self.canvas.draw()

    def getCanvas(self):
        return self.canvas.get_tk_widget()     # returns the canvas widget allowing it to be placed in a tkinter frame

    def draw(self):
        self.figure.set_figwidth(self.figwidth)      # dynamically updates the figure size allowing multiple sizes
        self.figure.set_figheight(self.figheight)    # of the same canvas object to be placed on different displays tabs
        self.canvas.draw()


if __name__ == "__main__":
    # sets up a simulation to run when 'simulation.py' is ran by itself to allow for easier testing of its functions
    country = gb.Country(["Country", "Null", "None", 10000, 100, 10])
    disease = gb.Disease(["COVID-19", 2.8, 0.006, 5, 9, 1, 0, "No Information", "No Information"])
    sim = Simulation(country, disease)   # creates a simulation object with defined country and disease
    sim.runSimulation(100)               # runs 100 timesteps of the simulation
    sim.plotSingleGraph()                # displays the graph of the simulation
