# Written by Christian Piper
# First Robotics Team 834
# Created: 12/22/20

# Import libraries
from xml.etree import ElementTree
import common_functions
import argparse
import ndjson
import os

# Constants for later use
whitelist =    ['red_power_port_high_goal', 'blue_power_port_high_goal', 'power_cell']
convert_list = ['Goal',                     'Goal',                      'Power_Cell']

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
    
    # Loop through the files provided
    for filename in input_files:

        # Accumulator for later deletions out of the Pascal data
        invalid_objects = []

        # Get the structure of the XML
        tree = ElementTree.parse(os.path.join(filepath, filename))

        # Get the root of the XML
        root = tree.getroot()

        # Loop through to find the parameters that need to be changed
        for possible_object in root:

            # Fix the folder name
            if possible_object.tag == 'folder':

                # Only update it with JPEGImages if that's the new folder, otherwise, pull it from the path
                if prepare_dataset:
                    possible_object.text = "JPEGImages"
                else:
                    possible_object.text = os.path.basename(filepath)

            # Fix the image name
            elif possible_object.tag == 'filename':
                
                # Pull the old image name
                old_image_name = possible_object.text

                # Get the image's extension
                raw_filename, file_ext = os.path.splitext(old_image_name)

                # Adjust it, removing the .png and replacing it with .jpg
                new_filename = raw_filename + '.jpg'

                # Save the new value
                possible_object.text = new_filename

            # Fix the file path
            elif possible_object.tag == 'path':
                possible_object.text = os.path.join(filepath, filename)

            # Check for the objects in a file
            elif possible_object.tag == 'object':

                # We found an object!
                for object_parameter in possible_object:

                    # Get to the names of the objects
                    if object_parameter.tag == 'name':

                        # Check to see if the object is on the whitelist
                        current_whitelist_index = 0

                        # Reset the logic checker
                        valid_object = False
                        
                        # Loop through the whitelist to find if the name is valid
                        for whitelist_value in whitelist:

                            if object_parameter.text == whitelist_value:
                                # It's on the whitelist
                                valid_object = True

                                # Change the XML value
                                object_parameter.text = convert_list[current_whitelist_index]

                            # Increment the counter
                            current_whitelist_index = current_whitelist_index + 1

                        # Object is invalid, it needs to be deleted
                        if valid_object == False:
                            invalid_objects.append(possible_object)
                            
        # Remove the invalid objects
        for invalid_object in invalid_objects:
            root.remove(invalid_object)

        # Remove the old XML
        os.remove(os.path.join(filepath, filename))

        # Write out the new file if there is more than one object left (there are 6 parts to the root file normally)
        if len(root) >= 7:
            common_functions.build_ndjson_annotation()