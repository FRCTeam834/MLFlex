# Christian Piper
# 11/21/19
# This program will generate a GUI in which the user can input the parameters. 
# The parameters will be used to create a code file that can be run on any Linux machine

# TODO: Better comments, help tab and files, status bar

# Import GUI library and Picture Library
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from shutil import copy
import csv
import os
import platform
import webbrowser
import threading
import time
import generate_files

# Create GUI instance
gui = tk.Tk()

# Constants
maxTitles = 3
tagCount = 10
top_row_offset = 140
first_entry_box_offset = 20
row_spacing = 30
window_width = 900
window_height = 800
red_hex = "#ff0000"
green_hex = "#49ff00"
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"


# Variables, such as the entry, spin, and check boxes
fileDir = ""
tag = []
spin_box = []
tag_list = [] 
instance_list = []
raw_team_number = None
model_name = None
neural_compute_stick = tk.BooleanVar()
print_info = tk.BooleanVar()
streamer = tk.BooleanVar()
dashboard_confidence = tk.BooleanVar()
neural_compute_stick_checkbox = None
print_info_checkbox = None
streamer_checkbox = None
dashboard_confidence_checkbox = None
export_title = None
status_bar_canvas = None
status_bar = None
status_line = None

# Assign the current directory
currentDir = os.path.dirname(os.path.abspath(__file__))

def main():
    # Setup the GUI
    setupGUI()

    gui_task = threading.Thread(target = gui.mainloop())
    #status_bar_task = threading.Thread(target = checkValues())

    gui_task.start
    #status_bar_task.start


def setupGUI():
    """Function to generate the GUI"""

    # Get the operating system for platform-based sizes
    os_name = platform.system()

    # Windows parameters
    if os_name == "Windows":
        text_font = "Helvetica 10"
        bold_text_font = "Helvetica 10 bold"
        tag_box_width = 29
        team_num_title_x = 420
    
    # Mac parameters
    elif os_name == "Mac":
        text_font = "Helvetica 14"
        bold_text_font = "Helvetica 14 bold"
        tag_box_width = 20
        team_num_title_x = 400

    # Default parameters if system isn't Mac or Windows
    else:
        text_font = "Helvetica 14"
        bold_text_font = "Helvetica 14 bold"
        tag_box_width = 20
        team_num_title_x = 400
    
    # Get the universal width and height
    global window_width
    global window_height

    # Setup window title and size
    gui.title("Edge Vision System Code Generator")
    gui.geometry(str(window_width) + "x" + str(window_height))

    # Declare description variable so that the code isn't cluttered with long text
    description = getTextFile("/resources/text/description.txt")

    # Description text
    createLabel(description, 350, 0, 525, 'l', text_font)  

    # Logo image
    createImage('/resources/images/logoNoBack.png', 0, 0, .5)

    # Tag title
    createLabel("Tags (from neural network)", 5, top_row_offset, 200, 'c', bold_text_font)

    # Tag Boxes
    tag_spacing = row_spacing
    list_start = top_row_offset + first_entry_box_offset
    
    # Create entry instances and add them to the tag array for later use
    global tag
    for entry in range(0, tagCount - 1):
        tag.append(CreateEntry(5, (list_start + (tag_spacing * entry)), True, width = tag_box_width))

    # SpinBox label
    createLabel("Maximum Instances:", 240, top_row_offset, 200, 'c', bold_text_font)

    # SpinBoxes for max instances
    spin_box_spacing = row_spacing
    spin_box_list_start = top_row_offset + first_entry_box_offset
    
    # Create box instaces and add them to spin_box array for use later
    global spin_box
    for entry in range(0, tagCount - 1):
        spin_box.append(CreateSpinBox(3, 0, 10, 240, (spin_box_list_start + (spin_box_spacing * entry)), True))

    # Team number title
    createLabel("Team Number:", team_num_title_x, top_row_offset, 200, 'c', bold_text_font)

    # Team number entry box
    global raw_team_number
    raw_team_number = CreateEntry(400, top_row_offset + first_entry_box_offset, True)

    # Model name title
    createLabel("Model Name (ex. alwaysai/mobilenet_ssd)", 600, top_row_offset, 300, 'c', bold_text_font)

    # Model name box
    global model_name
    model_name = CreateEntry(600, top_row_offset + first_entry_box_offset, True)

    # Neural Compute Stick checkbox
    global neural_compute_stick
    global neural_compute_stick_checkbox
    neural_compute_stick_checkbox = tk.Checkbutton(gui, text="Using Neural Compute Stick?", var = neural_compute_stick)
    neural_compute_stick_checkbox.config(wraplength = 300)
    neural_compute_stick_checkbox.place(x = 390, y = 300)

    # Print info checkbox
    global print_info
    global print_info_checkbox
    print_info_checkbox = tk.Checkbutton(gui, text="Print running info? This most likely will not save any processing power by disabling", var = print_info)
    print_info_checkbox.config(wraplength = 300)
    print_info_checkbox.place(x = 390, y = 363)

    # Streamer checkbox
    global streamer
    global streamer_checkbox
    streamer_checkbox = tk.Checkbutton(gui, text="Use the streamer? This will cause a drop in framerate, but will be benefical for testing", var = streamer)
    streamer_checkbox.config(wraplength = 300)
    streamer_checkbox.place(x = 390, y = 426)

    # Dashboard confidence checkbox
    global dashboard_confidence
    global dashboard_confidence_checkbox
    dashboard_confidence_checkbox = tk.Checkbutton(gui, text="View and modify confidence threshold on the SmartDashboard? (Beta! Use at your own risk!)", var = dashboard_confidence)
    dashboard_confidence_checkbox.config(wraplength = 300)
    dashboard_confidence_checkbox.place(x = 390, y = 490)

    # Export title naming
    createLabel("Version Name:", 400, top_row_offset + (1 * row_spacing) + first_entry_box_offset + 10, 200, "c", bold_text_font)

    # Export title entry box
    global export_title
    export_title = CreateEntry(400, top_row_offset + (2 * row_spacing) + first_entry_box_offset, True)

    # Status bar box at the bottom of the window
    global status_bar_canvas
    global red_hex
    global green_hex

    '''
    status_bar_canvas = tk.Canvas(gui, width = window_width, height = window_height)
    status_bar = status_bar_canvas.create_rectangle(0, 0, 895, 100, outline = red_hex, fill = red_hex)
    status_bar_canvas.place(x = 0, y = 700)


    # Status bar message
    global status_line
    status_line = tk.Label(gui, text = "", justify = "center", font = text_font, bg = "#ff0000")
    status_line.place(x = 450, y = 750)
    '''
    # Load internal startup settings if they exist
    save_file_path = "../application/resources/loading_parameters/EVS_settings.csv"
    if os.path.exists(save_file_path):
        loadSettings(save_file_path)

        
    # Create menu
    main_menu = tk.Menu(gui)

    # Create the menu structure for the file tab
    file_menu = tk.Menu(main_menu, tearoff = 0)
    file_menu.add_command(label="Save settings to file", command = saveSettings)
    file_menu.add_command(label="Load settings from file", command = loadSettings)
    file_menu.add_separator()
    file_menu.add_command(label="Save settings for next launch", command = saveLoadingSettings)
    file_menu.add_command(label="Reset launch settings", command = deleteLoadingSettings)
    file_menu.add_separator()
    file_menu.add_command(label="Generate code files", command = generateFiles)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command = gui.quit)
    main_menu.add_cascade(label="File", menu = file_menu)

    # Create the menu structure for the help tab
    help_menu = tk.Menu(main_menu, tearoff = 0)
    help_menu.add_command(label="Our team", command = openTeamWebsite)
    main_menu.add_cascade(label="Help", menu = help_menu)

    # Apply the menu that was just created
    gui.config(menu = main_menu)


def getParameterValues():
    """Gets the values for all of the parameters, then returns them as an array"""

    # Load all of the universal values
    global raw_team_number
    global model_name
    global export_title
    global neural_compute_stick
    global print_info
    global streamer
    global dashboard_confidence

    # Get their values and save them in _val variables
    raw_team_number_val = raw_team_number.get()
    model_name_val = model_name.get()
    export_title_val = export_title.get()
    neural_compute_stick_val = neural_compute_stick.get()
    print_info_val = print_info.get()
    streamer_val = streamer.get()
    dashboard_confidence_val = dashboard_confidence.get()

    # Return them as an array
    return raw_team_number_val, model_name_val, export_title_val, neural_compute_stick_val, print_info_val, streamer_val, dashboard_confidence_val


def getTextFile(path):
    """Returns the contents of a text file"""

    global currentDir
    file = open(currentDir + path, "r")
    text = file.read()
    return text


def openTeamWebsite():
    """Opens our team's website"""
    webbrowser.open('https://team834.org')


def selectDir(title = "Select directory"):
    """Select directory and return the path of the directory"""

    while True:
        fileDir = filedialog.askdirectory(parent = gui, initialdir = "/",title = title)
        if os.path.exists(fileDir) or fileDir == "":
            break
        else:
            print("Select a valid directory!")

    return fileDir

# TODO: Make the selectFile function error check

def selectFile(title = "Select file", file_ext = None):
    """Same as select directory, but returns a file path as well"""

    if not file_ext == None:
        fileDir = filedialog.askopenfilename(parent = gui, initialdir = "/", title = title, defaultextension = file_ext)
    else:
        fileDir = filedialog.askopenfilename(parent = gui, initialdir = "/", title = title)
    return fileDir


def saveSettings(dir = None):
    """Save the current entered data into a .csv file"""

    # Select a directory
    if dir == None:
        dir = selectDir(title = "Select save location for settings:")
    
    # Check if the directory exists
    if os.path.exists(dir):

        # Store the settings in a .csv file
        with open(dir + '/EVS_settings.csv', mode='w+') as settingsFile:

            # Set the names of the first row (parameter row)
            parameter_field_names = ['team_num', 'model_name', 'export_title', 'neural_compute_stick', 'print_info', 'streamer', 'dashboard_confidence']
            parameter_writer = csv.DictWriter(settingsFile, fieldnames = parameter_field_names)

            # Set the names of the tag and instance rows
            tag_and_instance_field_names = ['tag', 'instance_number']
            tag_and_instance_writer = csv.DictWriter(settingsFile, fieldnames = tag_and_instance_field_names)

            # Import the global boxes
            global tag
            global spin_box

            # Get the parameters
            parameters = getParameterValues()

            # Write out the header, then the parameters
            parameter_writer.writeheader()
            parameter_writer.writerow({'team_num': parameters[0], 'model_name' : parameters[1], 'export_title' : parameters[2],'neural_compute_stick': parameters[3], 'print_info': parameters[4], 'streamer': parameters[5], 'dashboard_confidence': parameters[6]})

            # Write out the second header, then the tag box and the spinbox values into each row
            tag_and_instance_writer.writeheader()
            for entry in range(0, tagCount - 1):
                tag_and_instance_writer.writerow({'tag': tag[entry].get(), 'instance_number': spin_box[entry].get()})

def saveLoadingSettings():
    """Saves the loading settings into the local directory"""

    saveSettings("./resources/loading_parameters/")

def deleteLoadingSettings():
    """Removes the past loading settings"""

    if os.path.exists("./application/resources/loading_parameters/EVS_settings.csv"):
        os.remove("./application/resources/loading_parameters/EVS_settings.csv")

def loadSettings(file = None):
    """Loads a .csv of all of the data"""

    # Select a directory if one isn't already selected
    if file == None:
        file = selectFile(title = "Select a parameter file to load the values from:", file_ext = ".csv")

    # Import global variables
    global tag
    global spin_box
    global raw_team_number
    global model_name
    global export_title
    global neural_compute_stick
    global print_info
    global streamer
    global dashboard_confidence
    global neural_compute_stick_checkbox
    global print_info_checkbox
    global streamer_checkbox
    global dashboard_confidence_checkbox

    # Check if the path exists, else the user has quited
    if os.path.exists(file):
        # Load the settings from a .csv file
        with open(file) as settings_file:

            # Read out the .csv file into a 2d array
            datareader = csv.reader(settings_file)
            data = []
            for row in datareader:
                data.append(row)

            # Set each of the tags and spinboxes to the correct amount
            for entry in range(0, 9):
                tag[entry].set(data[entry + 3][0])
                spin_box[entry].set(data[entry + 3][1])

            # Set the team number box
            raw_team_number.set(data[1][0])
            
            # Set the model box
            model_name.set(data[1][1])

            # Set the export name to it's values from the file
            export_title.set(data[1][2])

            # Toggle the checkboxes if they aren't in the correct state
            if not neural_compute_stick.get() == (data[1][3] == "True"):
                neural_compute_stick_checkbox.toggle()

            if not print_info.get() == (data[1][4] == "True"):
                print_info_checkbox.toggle()

            if not streamer.get() == (data[1][5] == "True"):
                streamer_checkbox.toggle()

            if not dashboard_confidence.get() == (data[1][6] == "True"):
                dashboard_confidence_checkbox.toggle()


def generateFiles():
    """Generates the code files based on input parameters"""

    if checkValues():

        # Import global variables
        global tag
        global tag_list
        global instance_list
        global raw_team_number
        global model_name
        global neural_compute_stick
        global print_info
        global streamer
        global dashboard_confidence

        # Get tags until one is empty
        for entry in range(0, len(tag)):
            tag_entry_value = tag[entry].get()
            if not tag_entry_value == "":
                tag_list.append(tag_entry_value)
                continue
            else:
                break

        # Set the instance list to the values in the spinboxes
        for entry in range(0, len(tag_list)):
            instance_list.append(spin_box[entry].get())

        raw_team_number_val = float(raw_team_number.get())

        # Get the value of all of the parameter boxes
        model_name_val = model_name.get()
        neural_compute_stick_val = neural_compute_stick.get()
        print_info_val = print_info.get()
        streamer_val = streamer.get()
        dashboard_confidence_val = dashboard_confidence.get()

        # Generate the Python and Java file contents and save them as a string
        python_file_contents = generate_files.generatePythonFile(tag_list, instance_list, raw_team_number_val, model_name_val, neural_compute_stick_val, print_info_val, streamer_val, dashboard_confidence_val)
        java_file_contents = generate_files.generateJavaFile(tag_list, instance_list)

        # Ask user for save directory, then write the code file there
        save_dir = selectDir(title = "Choose a directory for the output files:")
        
        # If the path exists, continue
        if os.path.exists(save_dir):

            # Check if the export directory exists already
            export_dir = save_dir + "/" + export_title.get()
            if not os.path.exists(export_dir):
                
                # If it doesn't create it
                os.mkdir(export_dir)

                # Create project directories
                raspi_dir = export_dir + "/RasPi_code"
                rio_dir = export_dir + "/Java_subsystem"
                os.mkdir(raspi_dir)
                os.mkdir(rio_dir)

                # Get all the files in the alwaysai companion files and see if they are valid
                companion_file_list = os.listdir("./resources/alwayai_companion_files/")

                # Copy the standard project files over
                for file in companion_file_list:
                    full_file_name = os.path.join("./resources/alwayai_companion_files/", file)
                    if os.path.exists(full_file_name):
                        copy(full_file_name, raspi_dir)

                # Save the Python file
                python_file = open(raspi_dir + "/app.py", mode = "w+")
                python_file.write(python_file_contents)

                # Save the java file
                java_file = open(rio_dir + "/EVSNetworkTables.java", mode = "w+")
                java_file.write(java_file_contents)

                # Print we finished
                print("Finished file export!")
            
            else:
                errorStatusBar("A folder with the same export name was found. Please choose another")
        
        else:
            errorStatusBar("The file path was not found")


def createImage(path, x_location, y_location, scale):
    """Creates an image"""

    # Import current directory
    global currentDir

    # Open the image
    image = Image.open( currentDir + path)

    # Find new dimensions based on scaling, then resize the image to those sizes
    width, height = image.size
    width = round(width * scale)
    height = round(height * scale)
    size = (width, height)
    resized = image.resize(size)

    # Create a Tk image out of the resized image, apply that to a Label, then place the label
    tk_image = ImageTk.PhotoImage( resized )
    img = tk.Label(gui, image = tk_image)
    img.image = tk_image
    img.place(x = x_location, y = y_location)


def createLabel(text, x_location, y_location, max_width, justification, font):
    """Creates a label at the specified location"""

    # Decide justification, or if justification should be used at all
    if justification == "l":
        justification = "left"
    elif justification == "r":
        justification = "right"
    elif justification == "c":
        justification = "center"

    # Decide if justification is specified
    if justification == None:
        label = tk.Label(gui, text = text, font = font, wraplength = max_width)
    else:
        label = tk.Label(gui, text = text, font = font, wraplength = max_width, justify = justification)
    
    # Place the label in the specified location
    label.place(x = x_location, y = y_location)


def errorStatusBar(text):
    global status_bar_canvas
    global status_bar
    global status_line
    global red_hex

    messagebox.showerror("Error building file", text)

    '''
    status_bar_canvas.itemconfig(status_bar, outline = red_hex, fill = red_hex)
    status_line.config(bg = red_hex, text = text)
    '''


def okStatusBar():
    global status_bar_canvas
    global status_bar
    global status_line
    global green_hex

    '''
    status_bar_canvas.itemconfig(status_bar, outline = green_hex, fill = green_hex)
    status_line.config(bg = green_hex, text = "All parameters are within bounds")
    '''

def checkForValidNames(string, valid_chars = None, first_line_valid_chars = None, invalid_chars = None):
    """ Makes sure that the string doesn't contain an invalid character"""

    string = str(string)

    issue_characters = []

    issue_found = False

    if not valid_chars == None:

        for character_num in range(0, len(string)):

            no_issue_found = False

            if not (first_line_valid_chars == None) and character_num == 0:
                for valid_character in first_line_valid_chars:
                    if string[character_num] == valid_character:
                        no_issue_found = True

            else:
                for valid_character in valid_chars:
                    if string[character_num] == valid_character:
                        no_issue_found = True

                        
            if no_issue_found == False:
                if string[character_num] == " ":
                    issue_characters.append("space")
                else:
                    issue_characters.append(string[character_num])


    elif not invalid_chars == None:

        for character_num in range(0, len(string)):
            for invalid_character in invalid_chars:
                if string[character_num] == invalid_character:
                    issue_found = True
                    issue_characters.append(string[character_num])

        if issue_found:
            dump_string = ""
            for entry in range(0, len(issue_characters)):
                dump_string = dump_string + issue_characters[entry] + ", "
            return dump_string
                    

    else:
        print("No valid or invalid selection")
        return -1

    dump_string = ""
    if not issue_characters == []:
        for entry in range(0, len(issue_characters)):
            if entry == (len(issue_characters) - 1):
                dump_string = dump_string + issue_characters[entry]
            else:
                dump_string = dump_string + issue_characters[entry] + ", "
        return dump_string
    else:
        return -1
    
    

def checkValues():
    """Checks the values, and changes the status bar at the bottom of the window to report errors"""

    # TODO: Spinbox error checking

    global tag
    global spin_box
    global raw_team_number
    global model_name
    global status_bar_canvas
    global status_line

    tag_flag = -1
    spin_box_flag = -1

    export_title_val = export_title.get()
    export_title_char_check = checkForValidNames(export_title_val, valid_chars = alphabet)

    try: 
        pass
        #raw_team_number_int = int(raw_team_number)
    except:
        errorStatusBar("Make sure the team number is an integer")
        return False



    for entry in range(0, 9):
        spin_box_entry = spin_box[entry].get()

        if not(checkForValidNames(spin_box_entry, valid_chars = "0123456789") == -1):
            pass
            # TODO: Fix
            '''
            errorStatusBar("Make sure that tag #" + str(entry + 1) + " maximum instances is an integer")
            return False
            '''

        '''
        try: 
            spin_box_entry_int = int(spin_box[entry].get())
        except:
            errorStatusBar("Make sure that tag #" + str(entry + 1) + " maximum instances is an integer")
            return False
        '''

        if not (int(spin_box_entry) >= 0 and int(spin_box_entry) <= 10):
            errorStatusBar("Make sure that tag #" + str(entry + 1) + " is in the range of 1-10")
            return False


    for entry in range(0, tagCount - 1):
        tag_entry_value = str(tag[entry].get())
        tag_entry_char_check = checkForValidNames(tag_entry_value, valid_chars = alphabet + "0123456789", first_line_valid_chars = alphabet)

        if not tag_flag == -1:
            break

        if not tag_entry_char_check == -1:
            # TODO: Fix this
            """
            try:
                tag_entry_char_check = int(tag_entry_char_check)
                errorStatusBar("Make sure tag #" + str(entry + 1) + " doesn't start with a " + str(tag_entry_char_check) + "")
                return False
            except:
                errorStatusBar("Make sure tag #" + str(entry + 1) + " doesn't have a " + tag_entry_char_check + " in it")
                return False
            """

        if (not tag_entry_value == "") and spin_box[entry].get() == '0':
            errorStatusBar("Make sure that tag #" + str(entry + 1) + " has at least one instance, otherwise don't include it")
            return False
        
        elif tag_entry_value == "" and (not spin_box[entry].get() == '0'):
            errorStatusBar("Make sure that tag #" + str(entry + 1) + " has it's maximum instance values set to 0 when not used")
            return False
        
    if not tag_flag == -1:
        errorStatusBar("Make sure there are no numbers in tag #" + str(tag_flag + 1))
        return False

    if not type(raw_team_number.get()) == "int":
        if not(checkForValidNames(raw_team_number.get(), valid_chars = "0123456789") == -1):
            errorStatusBar("Make sure the team number is a valid integer")
            return False

        try:
            raw_team_number_val = int(raw_team_number.get())
        except:
            errorStatusBar("Make sure that the team number is an integer and not negative")
            return False

    if not(checkForValidNames(raw_team_number_val, valid_chars = "0123456789") == -1):
        errorStatusBar("Remove the " + checkForValidNames(raw_team_number_val, valid_chars = "0123456789") + "in the team number")
        return False

    elif len(str(raw_team_number_val)) > 4 or raw_team_number_val  <= 0:
        errorStatusBar("Make sure you have a valid team number")
        return False

    elif not (export_title_char_check == -1):
        errorStatusBar("Make sure your export name doesn't have " + export_title_char_check + " in it")

    else:
        okStatusBar()
        return True


class CreateEntry:
    """Creates a tkniter entry box and the functions needed to manipulate it"""

    def __init__(self, x_location, y_location, visibility, width = 20):
        """Initializes the box"""
        self.entry = tk.Entry(gui)
        self.entry.config(width = width)
        if visibility == True:
            self.entry.place(x = x_location, y = y_location)
        self.entry.x = x_location
        self.entry.y = y_location

    def get(self):
        """Get the current value"""
        return self.entry.get()
    
    def set(self, value):
        """Set the value"""
        self.entry.delete(0, len(self.entry.get()))
        self.entry.insert(0, value)

    def hide(self):
        """Hide the entry"""
        self.entry.place_forget()

    def show(self):
        """Show the entry"""
        self.entry.place(x = self.entry.x, y = self.entry.y)


class CreateSpinBox:
    """Creates a tkinter spinbox and functions to manipulate it"""

    def __init__(self, width, from_, to, x_location, y_location, visibility):
        """Create the spinbox"""

        self.spinbox = tk.Spinbox(gui, from_ = from_, to = to, width = width)
        if visibility == True:
            self.spinbox.place(x = x_location, y = y_location)
        self.spinbox.x = x_location
        self.spinbox.y = y_location

    def get(self):
        """Get the current value of the spinbox"""

        return self.spinbox.get()

    def set(self, int_value):
        """Set the value of the spinbox"""

        self.spinbox.delete(0)
        self.spinbox.insert(0, int_value)

    def hide(self):
        """Hide the spinbox"""

        self.spinbox.place_forget()

    def show(self):
        """Show the spinbox"""

        self.spinbox.place(x = self.spinbox.x, y = self.spinbox.y)


if __name__ == '__main__':
    main()