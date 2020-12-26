# Written by Christian Piper
# First Robotics Team 834
# Created: 12/22/20

# Import libraries
from xml.etree import ElementTree
import common_functions
import argparse
import ndjson
import shutil
import time
import os

# Main function, pulls args, preps output, then converts the files
def pascal2ndjson():
    
    # Initialize parser 
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool. Annotation manipulation program') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # Required (String) arguments
    required_args.add_argument("-i", "--input",  required = True, help = "Input path to the folder containing the PascalVOC annotations.")
    required_args.add_argument("-o", "--output", required = True, help = "Output path for the .zip file")

    # Optional (Boolean) arguments
    parser.add_argument("-c", "--cleanup",      action = "store_true", default = False, help = "If parameter is specified, then the input folder and files will be automatically deleted after use")
    parser.add_argument("-f", "--feedback",     action = "store_true", default = True,  help = "If parameter is specified, then the feedback will be provided during the conversion process")
    
    # Read arguments from command line 
    args = parser.parse_args()

    # Get the start time
    start_time = time.time()

    # Get the full paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    # Delete the directory if it exists
    if os.path.exists(os.path.join(output_path, "Annotations")):
        shutil.rmtree(os.path.join(output_path, "Annotations"))

    # Create a directory for the annotations, then set the filepath to it.
    os.mkdir(os.path.join(output_path, "Annotations"))
    filepath = os.path.join(output_path, "Annotations")

    # Get all of the files in the input directory
    input_files = os.listdir(input_path)
    
    # Create an accumulator for counting the current file
    if args.feedback:
        current_file_index = 1
    
    # Loop through the files provided
    for filename in input_files:

        # Get all of the objects in the array
        image_objects = common_functions.get_PascalVOC_objects(filename, input_path)

        # Create an ndjson with the object array
        common_functions.build_ndjson_annotation(image_objects, filename, os.path.join(output_path, "Annotations"))

        # Only give feedback if needed
        if args.feedback:

            # Print out the current status
            print("Current file: " + str(current_file_index) + " out of " + str(len(input_files)))

            # Change the counter
            current_file_index =+ 1

    # Cleanup the files if specified
    if args.cleanup:
        shutil.rmtree(input_path)

    # Get the total time
    total_time = time.time() - start_time
    
    # Print total time to convert
    if args.feedback:
        
        # Print the feedback
        print("Total time to convert: " + str(round(total_time, 4)) + " seconds")


# Run the main function
pascal2ndjson()