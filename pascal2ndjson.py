# Written by Christian Piper
# First Robotics Team 834
# Created: 12/22/20

# Import libraries
from xml.etree import ElementTree
import common_functions
import argparse
import ndjson
import os

# Main function, pulls args, preps output, then converts the files
def pascal2ndjson():
    
    # Initialize parser 
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool. Annotation manipulation program') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # Required (String) arguments
    required_args.add_argument("-i", "--input",  required = True, help = "Input path to the folder containing the Supervisely annotations.")
    required_args.add_argument("-o", "--output", required = True, help = "Output path for the .zip file")

    # Optional (Boolean) arguments
    parser.add_argument("-j", "--join",         action = "store_true", default = False, help = "If parameter is specified, then if multiple Supervisely projects exist in the same folder, they will be joined into a single .zip instead of individual .zip files")
    parser.add_argument("-c", "--cleanup",      action = "store_true", default = False, help = "If parameter is specified, then the input Supervisely path will be automatically deleted after use")
    parser.add_argument("-d", "--debug",        action = "store_true", default = False, help = "If parameter is specified, then the temporary folders will be left for examination")
    parser.add_argument("-f", "--feedback",     action = "store_true", default = True,  help = "If parameter is specified, then the feedback will be provided during the conversion process")
    parser.add_argument("-a", "--augmentation", action = "store_true", default = False,  help = "If parameter is specified, then additional flipped and cropped versions of the images and annotations will be included in the output")
    
    # Read arguments from command line 
    args = parser.parse_args()
    
    # Get the full paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    # Create a directory for the annotations, then set the filepath to it
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
        common_functions.build_ndjson_annotation()

        # Only give feedback if needed
        if args.feedback:

            # Print out the current status
            print("Current file: " + str(current_file_index) + " out of " + str(len(input_files)))

            # Change the counter
            current_file_index =+ 1

    