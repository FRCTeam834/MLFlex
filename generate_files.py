# Christian Piper
# 12/4/19
# This code will generate a python file for the coprocessor to run

from re import sub
import argparse
import shutil
import os

# Create master strings
python_code = ""
java_code = ""
currentTagNum = 0


def main():

    # Initialize parser 
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool. Code file generator') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # Required Arguments
    required_args.add_argument("-t", "--tag_list",             required = True, nargs = '+', help = "List of objects (name)")
    required_args.add_argument("-i", "--instance_list",        required = True, nargs = '+', help = "Maximum allowed objects of each name")
    required_args.add_argument("-c", "--color_scheme",         required = True, nargs = '+', help = "List of box colors. Begins with default color then starts with the color of the bounding boxes for the first object. In BGR format, with color intensity being from 0-255")
    required_args.add_argument("-n", "--team_number",          required = True, help = "The team number")
    required_args.add_argument("-m", "--model_name",           required = True, help = "The name of the model being used")
    required_args.add_argument("-o", "--output_path",          required = True, help = "Output path for the code files")
    
   
    # Optional Arguments
    parser.add_argument("--neural_compute_stick",       required = False, action = "store_true", default = False, help = "If we're using a compute stick accelerator")
    parser.add_argument("-p", "--no_printed_info",      required = False, action = "store_true", default = False, help = "Do you want the information to be not printed?")
    parser.add_argument("-s", "--streamer",             required = False, action = "store_true", default = False, help = "If you want to have a stream of the output (debugging only)")
    parser.add_argument("-d", "--dashboard_confidence", required = False, action = "store_true", default = False, help = "If you want to have the threshold on the Smart Dashboard")
    parser.add_argument("-ds", "--dashboard_streaming", required = False, action = "store_true", default = False, help = "If you want to have a labeled stream over NetworkTables")

    # Read arguments from command line 
    args = parser.parse_args()

    # Generate the Python file, then save it
    python_code = generatePythonFile(args.tag_list, args.instance_list, args.color_scheme, args.team_number, args.model_name, args.neural_compute_stick, args.no_printed_info, args.streamer, args.dashboard_confidence, args.dashboard_streaming)

    # Generate the Java file, then save it
    java_code = generateJavaFile(args.tag_list, args.instance_list)

    output_path = os.path.abspath(args.output_path)

    # If the path exists, continue
    if os.path.exists(output_path):

        # Combine the path for the for the output folders
        raspi_dir = os.path.join(output_path, "RasPi")
        rio_dir = os.path.join(output_path, "Rio")

        # Delete the folders if they exist
        if os.path.exists(raspi_dir):
            shutil.rmtree(raspi_dir)

        if os.path.exists(rio_dir):
            shutil.rmtree(rio_dir)

        # Make the directories
        os.mkdir(raspi_dir)
        os.mkdir(rio_dir)

        if args.dashboard_streaming:
            companion_file_directory = "./resources/alwaysai_companion_files/standard_setup/"
        else:
            companion_file_directory = "./resources/alwaysai_companion_files/no_dashboard_stream/"

        # Get all the files in the AlwaysAi companion files and see if they are valid
        companion_file_list = os.listdir(companion_file_directory)

        # Copy the standard project files over
        for file_ in companion_file_list:
            full_file_path = os.path.join(os.path.abspath(companion_file_directory), file_)
            shutil.copy(full_file_path, raspi_dir)

        # Save the Python file
        python_file = open(os.path.join(raspi_dir, "app.py"), mode = "w+")
        python_file.write(python_code)

        # Save the java file
        java_file = open(os.path.join(rio_dir, "EVSNetworkTables.java"), mode = "w+")
        java_file.write(java_code)

        # Print we finished
        print("Finished file export!")
    
    else:
        print("The output path is not valid, please try another path")


# Parameter            : Description                                                : Example
# tag_list             : List of objects (name)                                     : [Goal, Power_Cell]
# instance_list        : Maximum allowed objects of each name                       : [1, 10]
# team_number          : The team number                                            : 834
# model_name           : The name of the model being used                           : cap1sup/test
# neural_compute_stick : If we're using a compute stick accelerator                 : Yes (usually)
# print_info           : Do you want to print info (for debugging)                  : No (usually)
# streamer             : If you want to have a stream of the output, debugging only : No (usually)
# dashboard_confidence : If you want to have the threshold on the Smart Dashboard?  : Does work :)

def generatePythonFile(tag_list, instance_list, color_scheme, team_number, model_name, neural_compute_stick, print_info, streamer, dashboard_confidence, dashboard_streaming):
    """Generates a Python file with the input parameters"""
   
    # Convert the instance list integers
    for entry in range(0, len(instance_list)):
        try:
            instance_list[entry] = int(instance_list[entry])
        except:
            print("Invalid instance number, output might not be valid")

    # Convert the team number to an int as well
    try:
        team_number = int(team_number)
    except:
        print("Invalid team number, output might not be valid")

    pythonAddString( 
    """import time
import edgeiq
from networktables import NetworkTables""")

    if dashboard_streaming:
        pythonAddString('\nfrom cscore import CameraServer')
    
    pythonAddString("""\nimport logging
import numpy as np
""")

    pythonAddString("\n# Constants")
    pythonAddString("\ndefault_conf_thres = .25")
    
    if dashboard_streaming:
        pythonAddString("""\ndefault_width = 640
default_height = 320""")
    
    pythonAddString(
"""\n\ndef main():
    # Allow Rio to boot and configure network
    time.sleep(10.0)

    # Setup logging for the NetworkTables messages
    logging.basicConfig(level=logging.DEBUG)

    # Setup NetworkTables
    NetworkTables.initialize(server = '10."""
    )

    # Convert team number into ip address format
    if team_number < 1000:
        string_team_number = str(team_number)
        formatted_team_number = string_team_number[0] + "." + string_team_number[1] + string_team_number[2]
    else:
        string_team_number = str(team_number)
        formatted_team_number = string_team_number[0] + string_team_number[1] + "." + string_team_number[2] + string_team_number[3]
        
    pythonAddString(
        formatted_team_number
    )

    pythonAddString(
        """.2')

    # Wait for the Pi to connect to the Rio
    while(not NetworkTables.isConnected()):
        time.sleep(0.5)
    
    # Set the update rate too slow so it doesn't mess with the flush commands
    NetworkTables.setUpdateRate(1)

    # Create table for values
    EVS = NetworkTables.getTable('EVS')
    sd = NetworkTables.getTable('SmartDashboard')

    # Set default values
    EVS.putBoolean('run_vision_tracking', True)""")

    if dashboard_confidence:
        pythonAddString("\n    EVS.putNumber('confidence_thres', default_conf_thres)")

    if dashboard_streaming:
        pythonAddString("""\n    EVS.putNumber('stream_width', default_width)
    EVS.putNumber('stream_height', default_height)""")

    pythonAddString("""\n\n    # Create sub-tables and append them to arrays
""")

    
    subtables_string = ""
    
    for tag_entry in range(0, len(tag_list)):
        if tag_entry == 0:
            subtables_string = subtables_string + "    " + tag_list[tag_entry] + "Tables = []"
        else:
            subtables_string = subtables_string + " \n\n    " + tag_list[tag_entry] + "Tables = []"
        for instance_entry in range(0, instance_list[tag_entry]):
            subtables_string = subtables_string + "\n"
            subtables_string = subtables_string + "    " + tag_list[tag_entry] + str(instance_entry) + " = EVS.getSubTable('" + tag_list[tag_entry] + str(instance_entry) + "')"
            subtables_string = subtables_string + "\n    " + tag_list[tag_entry] + "Tables.append(" + tag_list[tag_entry] + str(instance_entry) + ")"

    pythonAddString(subtables_string)
    pythonAddString('''\n
    # Setup EdgeIQ
    obj_detect = edgeiq.ObjectDetection("''' + model_name + '''")
    obj_detect.load(engine = edgeiq.Engine.DNN''')


    if neural_compute_stick == True:
        pythonAddString("_OPENVINO")

    pythonAddString(")")

    pythonAddString("""

    # Setup color values for objects (in BGR format), and then combine them to a single scheme
    default_color = (""" + color_scheme[0] + ", " + color_scheme[1] + ", " + color_scheme[2] + """)
    color_map = {\n""" )
    if not len(color_scheme) % 3 == 0:
        # We bad
        raise NameError("Make sure the color scheme is valid")

    if not (len(color_scheme) / 3) - 1 == len(tag_list):
        # We bad again
        raise NameError("Make sure the color scheme has the same number of color sets as the tag list")
        
    for object_index in range(0, len(tag_list)):
        if object_index == len(tag_list) - 1:
            # Last line doesn't need a comma
            comma = ""
        else:
            comma = ","
            
        pythonAddString("        " + ("\"") +  tag_list[object_index] + ("\"") + ":" + " (" + color_scheme[3 + object_index * 3] + ", " + color_scheme[4 + object_index * 3] + ", " +  color_scheme [5 + object_index * 3] + ")" + comma + "\n")
    
    pythonAddString("""    }
    colors = [color_map.get(label, default_color) for label in obj_detect.labels]""")
    

    if print_info == True:
        pythonAddString('''\n \n''')
        pythonAddString('''
    # Print out info
    print("Loaded model:\\n{}\\n".format(obj_detect.model_id))
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\\n".format(obj_detect.accelerator))
    print("Labels:\\n{}\\n".format(obj_detect.labels))''')

    pythonAddString('''\n
    # Get the FPS
    fps = edgeiq.FPS()
    
    # Setup the tracker for 20 frames deregister time and have a matching tolerance of 50
    tracker = edgeiq.CentroidTracker(deregister_frames = 20, max_distance = 50)
''')
    if dashboard_streaming:
        pythonAddString('''
    # Setup video cam feed
    cs = CameraServer.getInstance()
    cs.enableLogging()
    outputStream = cs.putVideo("Vision_Out", 300, 300)\n''')

    pythonAddString('''
    try:
        with edgeiq.WebcamVideoStream(cam = 0) as video_stream''')

    if streamer == True:
        pythonAddString(""", \\
                edgeiq.Streamer() as streamer""")

    pythonAddString(""": \n            
            # Allow Webcam to warm up
            time.sleep(2.0)""")
    pythonAddString("""
            fps.start()""")

    for entry in range(0, len(tag_list)):
        pythonAddString('''\n
            for i in range(0,''' + str(instance_list[entry] - 1) + '''): \n''')
        pythonAddString('''                ''' + tag_list[entry] + '''Tables[i].putBoolean('inUse', False)''')

    pythonAddString("""\n
            # loop detection
            while True:
""")

    pythonAddString("""
                # Pull a frame from the camera
                frame = video_stream.read()

                # Check to see if the camera should be processing images
                if (EVS.getBoolean('run_vision_tracking', True)):
                    
                    # Process the frame
                    results = obj_detect.detect_objects(frame, confidence_level = """)
    if dashboard_confidence:
        pythonAddString("EVS.getNumber('confidence_thres', default_conf_thres))\n")
    else:
        pythonAddString("default_conf_thres)\n")
    
    if streamer:
        pythonAddString("                frame = edgeiq.markup_image(frame, tracked_objects, colors = obj_detect.colors)\n")
    
    pythonAddString("""
                    # Update the object tracking
                    objects = tracker.update(results.predictions)

                    # Counters - they reset after every frame in the while loop \n""")

    for entry in range(0, len(tag_list)):
        pythonAddString("                    " + str(tag_list[entry]) + "Counter = 0 \n")

    pythonAddString(''' 
                    # Define the collections variable
                    predictions = []

                    # Update the EVS NetworkTable with new values
                    for (object_id, prediction) in objects.items():                                                                                                                        

                        # Add current prediction to the total list
                        predictions.append(prediction)                                                                                                   

                        # Pull the x and y of the center
                        center_x, center_y = prediction.box.center

                        # Package all of the values as an array for export
                        number_values = [object_id, center_x, center_y, prediction.box.end_x, prediction.box.end_y, prediction.box.area, (prediction.confidence * 100)]
                        
                        # Round all of the values to the thousands place, as anything after is irrelevant to what we need to do
                        for entry in range(0, len(number_values) - 1):
                            number_values[entry] = round(number_values[entry], 3)

                        # Convert the values to a numpy array for exporting
                        number_values_array = np.asarray(number_values)  \n\n''')

    # Create the classifier
    for entry in range(0, len(tag_list)):
        if entry == 0:
            pythonAddString('''                        # Sort results into their respective classes
                        if prediction.label == "''' + tag_list[entry] + '":')

        else: 
            pythonAddString('                        elif prediction.label == "' + tag_list[entry] + '":')
    
        pythonAddString('''\n
                            # Make sure that we haven't exceeded the maximum number of objects per frame
                            if (''' + tag_list[entry] + 'Counter <= ' + str(instance_list[entry] - 1) + '''):
                                ''' + tag_list[entry] + '''Tables[''' + tag_list[entry] + '''Counter].putNumberArray('values', number_values_array)
                                # Boolean asks to update
                                ''' + tag_list[entry] + '''Tables[''' + tag_list[entry] + '''Counter].putBoolean('inUse', True)

                            # Increase the counter
                            ''' + tag_list[entry] + '''Counter += 1 \n\n''')
        

    pythonAddString("                    # Sets the value after the last value to false. The Rio will stop when it finds a False\n")

    for entry in range(0, len(tag_list)):
        pythonAddString('                    if (' + tag_list[entry] + 'Counter <= ' + str(instance_list[entry] - 1) + '''):
                        ''' + tag_list[entry] + 'Tables[' + tag_list[entry] + "Counter].putBoolean('inUse', False)\n\n")

    pythonAddString('''                    # Notify the Rio that vision processing is done, and the data is valid again
                    EVS.putBoolean('checked', False)\n\n''')

    if dashboard_streaming:
        pythonAddString('''                    # Do the frame labeling last, as it is lower priority
                    frame = edgeiq.markup_image(frame, results.predictions, colors=colors)\n\n''')

    pythonAddString('''                    # Flush all of the values to update on NetworkTables
                    NetworkTables.flush()\n\n''')

    # ! Needs checked
    if streamer:
        pythonAddString('''                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append("Inference time: {:1.3f} s".format(results.duration))
                text.append("Objects:")

                # Format and display values on localhost streamer
                for prediction in results.predictions:
                    text.append("{}: {:2.2f}%".format(
                        prediction.label, prediction.confidence * 100))

                streamer.send_data(frame, text))\n''')

    if dashboard_streaming:
        pythonAddString('''                # Get the streaming parameters
                width = EVS.getNumber('stream_width', default_width)
                height = EVS.getNumber('stream_height', default_height)

                # Resize the frame to the correct size
                frame = edgeiq.resize(frame, width, height)

                # Put stream on regardless of vision activation
                outputStream.putFrame(frame)\n\n''')
    
    pythonAddString('''                # Update the FPS tracker
                fps.update()\n\n''')
    
    if streamer:
        pythonAddString('''
                if streamer.check_exit():
                    break\n''')

    pythonAddString('''    finally:
        fps.stop()''')
    pythonAddString('''
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")\n''')

    pythonAddString('''
if __name__ == "__main__":
    main()''')


    # Pull python_code variable and print it
    global python_code
    print("Code Generated!")
    return python_code
    


def pythonAddString(string):
    """Adds strings to the master string for the python code"""

    global python_code
    python_code = python_code + string


def javaAddString(string):
    """Adds a string to the end of the master Java code"""

    global java_code
    java_code = java_code + string


def generateJavaFile(tag_list, instance_list):
    """Generates the Java code based on input paramters"""

    javaAddString("""/*----------------------------------------------------------------------------*/
/* Copyright (c) 2020 FIRST. All Rights Reserved.                             */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package frc.robot.subsystems;

import java.util.ArrayList;

import edu.wpi.first.networktables.NetworkTable;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj.command.Subsystem;

/**
 * Data structure for returned arrays is as follows: 
 * - Each column (first value) represents a space to store object values. 
 * The data structure of the rows is
 * as follows: - 0 or -1, with -1 being not used and 0 being used (meaning data
 * is valid and should be considered) 
 * - centerX - the x coordinate of the center
 * - centerY - the y coordinate of the center 
 * - endX - the x coordinate of the bottom right corner of the bounding box 
 * - endY - the y coordinate of the bottom right corner of the bounding box 
 * - area - the area of the bounding box
 * - confidence - the confidence level of the neural network that the object is indeed what it is tagged as
 */

public class EVSNetworkTables extends Subsystem {
  // Put methods for controlling this subsystem
  // here. Call these from Commands.

  NetworkTableInstance networkTableInstance = NetworkTableInstance.getDefault();

  @Override
  public void initDefaultCommand() {
    // Set the default command for a subsystem here.
    // setDefaultCommand(new MySpecialCommand());
    
  }

  public NetworkTable getVisionTable() {

    evs = networkTableInstance.getTable("EVS");
    return evs;

  }
""")

    for tag_num in range(0, len(tag_list)):

        raw_method_name = tag_list[tag_num]
        pascal_name = ''.join(x.capitalize() or '_' for x in raw_method_name.split('_'))
        raw_method_name = sub(r"(_|-)+", " ", raw_method_name).title().replace(" ", "")
        camel_name = raw_method_name[0].lower() + raw_method_name[1:]
        
        javaAddString('''
  public ArrayList<double[]> get''' + pascal_name + '''Array() {

    // Create a new expandable array for the tables
    ArrayList<double[]> visionArray = new ArrayList<double[]>();

    // Loop through the available objects
    for (int objectCount = 0; objectCount < ''' + str(instance_list[tag_num]) + '''; objectCount++) {
      
      // Create the name for the object
      String objectName = "''' + tag_list[tag_num] + '''" + objectCount;
      
      // Check if the entry is valid
      if (getVisionTable().getSubTable(objectName).getEntry("inUse").getBoolean(true)){

        // Create a new array for the values from NetworkTables
        double ''' + camel_name + '''Array[] = getVisionTable().getSubTable(objectName).getEntry("values").getDoubleArray(new double[7]);
  
        // Add the data for the object to the array
        visionArray.add(''' + camel_name + '''Array); 
        
      } else {
 
        // Break the loop if no object is found
        break;
        
      }
    }

    // Return our findings
    return visionArray;

  }
  ''')

    javaAddString("}")

    global java_code
    return java_code


# Call my boy main
if __name__ == "__main__":
    main()