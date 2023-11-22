import globalvars as gb

import tkinter as tk
import csv
from tkinter import ttk


# simplified copy of the 'App' class in 'main.py' only used when this file is ran by itself, allows for targeted testing
class PandemicApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        self.config(bg="white")
        container.pack(side="top", fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.resizable(False, False)

        self.currentPage = DiseaseSelectionPage

        self.title("Disease Selector")
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in [DiseaseSelectionPage]:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.showPage(DiseaseSelectionPage)

        # creates a style for the app so everything looks consistent
        simStyle = ttk.Style()
        simStyle.configure("TLabel", background=gb.bgcol)        # style for ttk.Label
        simStyle.configure("TFrame", background=gb.bgcol)        # style for ttk.Frame
        simStyle.configure("TScale", background=gb.bgcol)        # style for ttk.Scale
        simStyle.configure("TNotebook", background=gb.bgcol, border=0)                  # style for ttk.Notebook
        simStyle.configure("TCheckbutton", foreground="#09090A", background=gb.bgcol)   # style for ttk.Checkbutton

    def showPage(self, cont):
        gb.return_frame = self.currentPage
        frame = self.frames[cont]
        self.currentPage = cont
        frame.tkraise()


class DiseaseSelectionPage(ttk.Frame):

    def __init__(self, parent_frame, app):
        ttk.Frame.__init__(self, parent_frame)   # initializes the tkinter frame
        self.app = app                           # base app class

        # deafult values for a disease object, used when creating new diseases
        self.deafultDiseaseData = ["New Disease", 1, 0, 0, 1, 0, 1, "No Information", "No Information"]

        # organizes the widgets on the window
        ttk.Label(self, text="Select a Disease", font=gb.TITLEFONT).grid(row=0, column=0, columnspan=2, pady=10)
        leftframe = ttk.Frame(self)
        self.createTreeview(leftframe)
        buttonlabel = ttk.Label(leftframe)
        ttk.Button(buttonlabel, text="New Disease", width=12, command=self.newDisease).pack(side="left", pady=6)
        self.editbutt = ttk.Button(buttonlabel, text="Edit", width=8, state="disabled", command=self.editDisease)
        self.editbutt.pack(side="left", padx=3)
        self.delbutt = ttk.Button(buttonlabel, text="Delete", width=8, state="disabled", command=self.deleteDisease)
        self.delbutt.pack(side="left")
        buttonlabel.pack(side="left")
        self.addbutt = ttk.Button(leftframe, text="Add to Sim", command=self.addDiseaseToSim, state="disabled")
        self.addbutt.pack(pady=5, side="right", anchor="e", padx=19)
        leftframe.grid(row=1, column=0, padx=30, pady=10)
        self.rightframe = tk.Frame(self)
        self.configureFactFrame()

        tk.Button(self, text="🡰", width=6, command=self.back).place(x=10, y=10)

    def createTreeview(self, frame):
        ttk.Style().map('Treeview', background=[('selected', '#09090A')])    # changes bg colour of currently selected item on the table

        treeframe = tk.Frame(frame)

        # creates the treeview for the disease objects to be selected from
        treecolumns = ("R0 Value", "Mortality", "Incubation Period", "Infectious Period")
        self.table = ttk.Treeview(treeframe, columns=treecolumns, selectmode="browse", height=22, padding=1)
        # creates the main column and titles in 'Name'
        self.table.column("#0", width=170, minwidth=150)
        self.table.heading("#0", text="Name", anchor=tk.W)
        # loops through every column and assigns the sort function to each
        for col in treecolumns:
            self.table.column(col, width=len(col)*5+30, minwidth=50)
            self.table.heading(col, text=col, anchor=tk.W, command=lambda _col=col: self.sortClickedColumn(self.table, _col, True))

        # creates a scrollbar on the treeview for navigating when there are too many diseases to display on the screen
        ybar = ttk.Scrollbar(treeframe, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=ybar.set)
        ybar.pack(side="right", fill="y")

        # creates a dictionary of disease objects using their treeview id as a key while adding them to the treeview
        self.disease_dict = {}
        for i in range(len(disease_li)):
            self.addDisease(disease_li[i])    # adds a disease to the treeview and the dictionary

        self.table.bind("<Return>", self.addDiseaseToSim)                   # adds the disease to simulation when the enter key is pressed
        self.table.bind("<<TreeviewSelect>>", self.newDiseaseSelected)      # updates buttons and the info box when a new disease is clicked
        self.table.bind("<KeyRelease-Escape>", self.unselectDisease)        # removes the selection from the currently selected disease when 'esc' key pressed
        self.table.pack()

        self.table.tag_configure("custom", background="#F3F3F3")     # changes the background colour for all custom diseases to differentiate them

        treeframe.pack()

    def configureFactFrame(self):
        self.rightframe.grid_forget()         # removes the old frame from the window
        self.rightframe.destroy()             # destroys the old frame to improve performance and save memory
        self.rightframe = tk.Frame(self, width=330, height=470, bd=1)
        self.rightframe.pack_propagate(0)     # allows the width and height of the frame to be set
        self.rightframe.grid(row=1, column=1, sticky="n", padx=10, pady=10)

        if iid := self.table.focus():
            # when a disease is selected a fact frame is configured
            disease = self.disease_dict[iid]       # the disease object
            title = tk.Label(self.rightframe)
            namelabel = tk.Label(title, text=disease.name, font=gb.SUBFONT)
            namelabel.pack()

            # dynamically edits the font size of the disease name to allow for every name to fit inside the fact frame
            fontsize = 23
            self.app.update_idletasks()
            while namelabel.winfo_reqwidth() > 300:                     # loops until the name label fits inside the frame
                fontsize -= 1                                           # lowers the font size
                namelabel.config(font=("Verdana", fontsize, "bold"))    # changes the font
                self.app.update_idletasks()                             # updates idletasks to draw it onto the screen so pixels can be checked

            if disease.custom:
                customtxt = "Custom Disease"
            else:
                customtxt = "Built-In Disease"
            tk.Label(title, text=customtxt, font=gb.MEDFONT).pack()
            title.place(relx=0.5, y=20, anchor="n")
            info = tk.Label(self.rightframe)
            tk.Label(info, text="R0 Value:", font=gb.MIDFONT).grid(row=0, column=0, sticky="e", pady=1)
            tk.Label(info, text=disease.r0, font=gb.MIDFONT).grid(row=0, column=1, sticky="w", padx=2)
            tk.Label(info, text="Mortality Rate:", font=gb.MIDFONT).grid(row=1, column=0, sticky="e", pady=1)
            tk.Label(info, text=disease.dpercent, font=gb.MIDFONT).grid(row=1, column=1, sticky="w", padx=2)
            tk.Label(info, text="Incub. Period:", font=gb.MIDFONT).grid(row=2, column=0, sticky="e", pady=1)
            tk.Label(info, text=str(disease.incubation)+" days", font=gb.MIDFONT).grid(row=2, column=1, sticky="w", padx=2)
            tk.Label(info, text="Infection Time:", font=gb.MIDFONT).grid(row=3, column=0, sticky="e", pady=1)
            tk.Label(info, text=str(disease.infectious)+" days", font=gb.MIDFONT).grid(row=3, column=1, sticky="w", padx=2)
            info.place(x=50, y=106, anchor="nw")

            about = tk.Label(self.rightframe)
            tk.Label(about, text="About:", font=gb.MIDFONT).pack()
            tk.Message(about, text=disease.about, width=290, font=gb.MEDFONT, justify="center").pack(pady=1)
            about.place(relx=0.5, y=235, anchor="n")
            history = tk.Label(self.rightframe)
            tk.Label(history, text="History:", font=gb.MIDFONT).pack()
            tk.Message(history, text=disease.history, width=290, font=gb.MEDFONT, justify="center").pack(pady=1)
            history.place(relx=0.5, y=344, anchor="n")
        else:
            # if no disease is selected the frame promts the user to select one
            chooselabel = tk.Label(self.rightframe, text="Please select a disease", font=gb.BIGFONT)
            chooselabel.pack(fill="both", expand=True)

    def addDiseaseToSim(self, *args):
        # if there is a currently selected disease
        if self.table.focus():
            disease = self.disease_dict[self.table.focus()]   # the disease object is got from the disease dictoinary using its table id
            addToSimulation(disease)                          # the disease is added to the simualtion
            self.unselectDisease()                            # it is unselected from the table
            self.app.showPage(gb.return_frame)                # the app returns to the previous page

    def newDisease(self):
        # creates a new deafult disease object and passes it to the edit disease function to allow the user to edit it
        new_disease = gb.Disease(self.deafultDiseaseData)
        self.editDisease(disease=new_disease)

    def editDisease(self, disease=None):
        # will edit the currently selected disease if no disease object is passed to the function
        if not disease:
            iid = self.table.focus()
            disease = self.disease_dict[iid]
        else:
            iid = ""

        # if the disease is not already a custom disease, a new custom disease object is created with the existing data, but '(Custom)' is added to the name
        if not disease.custom:
            data = [disease.name+" (Custom)", disease.r0, disease.drate, disease.incubation, disease.infectious, disease.respiritory, 1, disease.about, disease.history]
            disease = gb.Disease(data)
            iid = ""

        # if there is already a disease information popup, it is destroyed
        try:
            self.editpopup.destroy()
        except AttributeError:
            pass

        # creates a popup window and places the disease edit page for the selected disease
        self.editpopup = tk.Toplevel(self.master)
        DiseaseEditPage(self, self.editpopup, disease, iid)

    def deleteDisease(self):
        item_id = self.table.focus()                       # gets the table id of the currently selected disease
        self.table.delete(item_id)                         # deletes the entry from the table
        disease_li.remove(self.disease_dict[item_id])      # removes the disease object from the disease object list
        writeNewCSV()                                      # updates the csv file
        self.newDiseaseSelected()                          # updates the buttons info section on the right

    def unselectDisease(self, *args):
        # finds the table id of the currently selected diseases and removes focus from them
        for iid in self.table.selection():
            self.table.selection_remove(iid)
            self.table.focus("")
        self.newDiseaseSelected()       # updates the buttons and info section on the right

    def addDisease(self, disease, index="end"):
        # index can be specified when putting diseases into specific rows of the table eg- when saving an edit
        # tuple of disease values that match the table headings
        values = (disease.r0, disease.dpercent, disease.incubation, disease.infectious)
        if disease.custom:
            tag = "custom"
        else:
            tag = "all"
        # adds the disease and stores its table id
        tmpid = self.table.insert("", index, text=disease.name, values=values, tags=tag)
        # adds a reference to the disease object with the id as the key to a dictionary
        self.disease_dict[tmpid] = disease
        return tmpid

    def newDiseaseSelected(self, *args):
        # checks if a disease is currently selected and changes the buttons usability accordingly
        if iid := self.table.focus():
            self.editbutt["state"] = "normal"          # when one is selected 'edit' and 'add' buttons are enabled
            self.addbutt["state"] = "normal"
            if self.disease_dict[iid].custom:          # if the selected disease is a custom disease the 'delete' button is enabled
                self.delbutt["state"] = "normal"
            else:
                self.delbutt["state"] = "disabled"
        else:
            self.editbutt["state"] = "disabled"        # when no disease is selected all buttons are disabled
            self.delbutt["state"] = "disabled"
            self.addbutt["state"] = "disabled"

        self.configureFactFrame()       # the info section on the right is updated

    def sortClickedColumn(self, tree, col, reverse):
        # function takes perameters of: the table widget, the column being sorted, whether to sort reverse
        column_list = [(tree.set(k, col), k) for k in tree.get_children('')]       # creats a list of tuples in the form (item, item id) to be sorted
        sorted_list = self.smartSort(column_list, reverse)                         # sorts the list using a custom function for different data types

        for index, (val, k) in enumerate(sorted_list):        # loops through the list to reorder the table
            tree.move(k, '', index)                           # moves each item to its new index, '' means the item is not moved into a subfolder

        # changes the command for the column to reverse the order next time its sorted
        tree.heading(col, command=lambda _col=col: self.sortClickedColumn(tree, _col, not reverse))

    def smartSort(self, unsorted_list, reverse):
        first = unsorted_list[0][0]                 # gets the first item in the list to determine the format/data type
        if first.endswith("%"):                                                                     # if the list is in the form of a percentage...
            sorted_list = sorted(unsorted_list, reverse=reverse, key=lambda x: float(x[0][:-1]))    # sorts as a float ignoring the percentage sign
        else:
            try:
                float(first)                                                                        # if the item can be converted to a float
                sorted_list = sorted(unsorted_list, reverse=reverse, key=lambda x: float(x[0]))     # the column is sorted with each item as a float
            except ValueError:
                sorted_list = sorted(unsorted_list, reverse=reverse)                                # otherwise its sorted normally ie- alphabetically

        return sorted_list

    def back(self):
        self.app.showPage(gb.return_frame)


class DiseaseEditPage():

    def __init__(self, master, top, disease, iid):
        self.master = master           # main disease page
        self.top = top                 # popup window
        # places the new window in a set place relative to the main window position and makes in non-resizable
        tmpx, tmpy = self.master.app.winfo_x(), self.master.app.winfo_y()
        geo = f"310x450+{tmpx+130}+{tmpy+100}"
        self.top.geometry(geo)
        self.top.resizable(False, False)

        self.top.title("Edit Disease")
        self.frame = tk.Frame(self.top)  # main frame for widgets
        self.frame.pack()
        self.disease = disease   # stores disease object
        self.iid = iid           # stores id of disease for the treeview

        # tkinter variables for storing and editing disease objects
        self.name = tk.StringVar(value=disease.name)
        self.r0 = tk.StringVar(value=round(disease.r0, 1))
        self.drate = tk.StringVar(value=round(disease.drate*100, 4))
        self.incubation = tk.StringVar(value=disease.incubation)
        self.infectious = tk.StringVar(value=disease.infectious)

        # organizes the widgets
        tk.Entry(self.frame, textvar=self.name, font=gb.BIGFONT, justify="center").pack(pady=15)
        self.name.trace("w", lambda *args: self.entryValidation(self.name, 23))
        infoentry = tk.Frame(self.frame)
        tk.Label(infoentry, text="R0 Value:", font=gb.MEDFONT).grid(row=0, column=0, sticky="e", pady=2)
        tk.Entry(infoentry, textvar=self.r0, font=gb.MEDFONT, width=8).grid(row=0, column=1, columnspan=2, sticky="w", padx=5)
        self.r0.trace("w", lambda *args: self.entryValidation(self.r0, 8, entrytype="decimal"))
        tk.Label(infoentry, text="Mortality:", font=gb.MEDFONT).grid(row=1, column=0, sticky="e", pady=2)
        tk.Entry(infoentry, textvar=self.drate, font=gb.MEDFONT, width=6).grid(row=1, column=1, sticky="w", padx=5)
        self.drate.trace("w", lambda *args: self.entryValidation(self.drate, 6, entrytype="percentage"))
        tk.Label(infoentry, text="%", font=gb.MEDFONT).grid(row=1, column=2, sticky="w")
        tk.Label(infoentry, text="Incubation Period:", font=gb.MEDFONT).grid(row=2, column=0, sticky="e", pady=2)
        tk.Entry(infoentry, textvar=self.incubation, font=gb.MEDFONT, width=4).grid(row=2, column=1, sticky="w", padx=5)
        self.incubation.trace("w", lambda *args: self.entryValidation(self.incubation, 3, entrytype="integer"))
        tk.Label(infoentry, text="Infection Len:", font=gb.MEDFONT).grid(row=3, column=0, sticky="e", pady=2)
        tk.Entry(infoentry, textvar=self.infectious, font=gb.MEDFONT, width=4).grid(row=3, column=1, sticky="w", padx=5)
        self.infectious.trace("w", lambda *args: self.entryValidation(self.infectious, 3, entrytype="integer"))
        infoentry.pack()

        self.warningtext = tk.StringVar()
        tk.Label(self.frame, textvar=self.warningtext, font=gb.MEDFONT).pack()

        tk.Label(self.frame, text="About:", font=gb.MEDFONT).pack()
        self.about = tk.Text(self.frame, width=26, height=4, font=gb.MEDFONT)
        self.about.insert("insert", disease.about)
        self.about.pack()
        # self.about.trace("w", lambda *args: self.entryValidation(self.about, 137))

        tk.Label(self.frame, text="History:", font=gb.MEDFONT).pack()
        self.history = tk.Text(self.frame, width=26, height=4, font=gb.MEDFONT)
        self.history.insert("insert", disease.history)
        self.history.pack()
        # self.history.trace("w", lambda *args: self.entryValidation(self.history, 137))

        buttons = tk.Label(self.frame)
        tk.Button(buttons, text="Cancel", width=6, command=self.top.destroy).grid(row=0, column=0, padx=40)
        tk.Button(buttons, text="Save", width=6, command=self.saveEdit).grid(row=0, column=1, padx=40)
        buttons.pack(pady=13)

    def saveEdit(self):
        # when saving a new diease, if any entries are empty then the deafult value for that section is used
        deafult = self.master.deafultDiseaseData
        if name := self.name.get():
            self.disease.name = name                            # saves the new name to the disease object
        else:
            self.disease.name = deafult[0]
        if r0 := self.r0.get():
            self.disease.r0 = round(float(r0), 2)               # saves the new r0 value to the disease object
        else:
            self.disease.r0 = round(float(deafult[1]), 2)
        if drate := self.drate.get():
            self.disease.drate = round(float(drate)/100, 6)     # saves the new mortality rate to the disease object
        else:
            self.disease.drate = round(deafult[2], 6)
        if inc := self.incubation.get():
            self.disease.incubation = int(inc)                  # saves the new disease incubation period
        else:
            self.disease.incubation = deafult[3]
        if inf := self.infectious.get():
            self.disease.infectious = int(inf)
        else:
            self.disease.infectious = deafult[4]                # saves the new disease infection period

        if about := self.about.get("1.0", "end").rstrip():        # saves the new about section, stiped of trailing spaces
            self.disease.about = about
        else:
            self.disease.about = deafult[7]
        if history := self.history.get("1.0", "end").rstrip():         # saves the new history section, stiped of trailing spaces
            self.disease.history = history
        else:
            self.disease.history = deafult[8]
        self.disease.makepercent()

        if self.iid:
            disease_li.remove(self.master.disease_dict[self.iid])     # previous disease object is remvoved from the disease list
            index = self.master.table.index(self.iid)                 # the row number of the old disease object
            self.master.table.delete(self.iid)                        # removed the old disease object from the table
            disease_li.insert(index, self.disease)                    # adds the new disease object back into the list
        else:
            index = "end"                                             # if the disease is new, the index is set to the end
            disease_li.append(self.disease)                           # the new disease is then appended to the disease list
        writeNewCSV()                                                 # writes new disease list to the csv
        iid = self.master.addDisease(self.disease, index=index)       # adds the new disease back into the table in the old index

        self.master.table.focus(iid)                 # sets the new disease as the one that is selected in the table
        self.master.table.selection_set(iid)
        self.master.table.focus_set()
        self.master.newDiseaseSelected()             # resets the fact file on the right to the new disease

        self.top.destroy()                           # closes the edit popup

    def entryValidation(self, entryvar, lim, entrytype=""):
        entry = entryvar.get()
        try:
            last = entry[-1]      # if there is no text in the entry then the function returns without doing anything
        except IndexError:
            return

        while entry[0] == "0" and len(entry) > 1 and entry[1] != ".":    # removed leading 0s unless it is decimal
            entry = entry[1:]
            entryvar.set(entry)

        if len(entry) > lim:                  # if the length of the entered text is longer than the max
            entryvar.set(entry[:lim])         # the entry is set to the limit
        elif entrytype == "integer":            # checked when the entry type is just an integer
            if not last.isdecimal():            # if the entered letter is not a number
                entryvar.set(entry[:-1])        # the entered number is removed
        elif entrytype:                                                               # otherwise, it is a decimal entry type
            if not last.isdecimal() and last != ".":                        # if the entered letter is not a number or a decimal point
                entryvar.set(entry[:-1])                                    # the entered number is removed
            elif last == "." and entry.count(".") > 1:                      # or if a decimal point is entered when there is already a decimal point
                entryvar.set(entry[:-1])                                    # the entered number is removed
            elif entrytype == "decimal" and entry.count(".") == 1:          # or for just decimal number entries,
                index = entry.index(".")                                    # the digits after the point is limited to 3
                entryvar.set(entry[:index+3])
            elif entrytype == "percentage" and entry.count(".") == 0:       # or if it is a percentage entry,
                entryvar.set(entry[:2])                                     # the numbers before the point is limited to 2 (less than 100%)


def createDiseaseList():
    disease_li = []
    with open("diseases.csv", "r") as f:            # opens the csv in read mode
        reader = csv.reader(f, delimiter=',')
        for row in reader:                          # loops through every disease in the csv
            disease_li.append(gb.Disease(row))         # appends a disease object created with the row information
    return disease_li


def writeNewCSV():
    with open("diseases.csv", "w", newline='') as f:     # opens the csv in write mode
        writer = csv.writer(f, delimiter=',')
        for disease in sorted(disease_li, key=lambda x: (x.custom, x.name)):     # writing rows to the csv alphabetically to maintain the order, with custom objects at the bottom
            writer.writerow([disease.name, disease.r0, disease.drate, disease.incubation, disease.infectious, disease.respiritory, disease.custom, disease.about, disease.history])


def addToSimulation(disease_object):
    # changes the correct simulation disease object in the globalvars.py file to the user selected disease
    if gb.simEditing == 1:
        gb.simDisease1 = disease_object
    elif gb.simEditing == 2:
        gb.simDisease2 = disease_object
    else:
        print("Error adding to simulation: Simulation is not currently editing a disease variable")


disease_li = createDiseaseList()


# allows the page to be ran by itself for easy testing of this part of the application
if __name__ == "__main__":
    tkapp = PandemicApp()
    tkapp.geometry("1000x600")
    tkapp.mainloop()
