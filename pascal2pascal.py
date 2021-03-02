# Written by Christian Piper
# First Robotics Team 834
# Created: 8/17/20

# Import libraries
import xml.etree.ElementTree as xml
from xml.etree import ElementTree
from xml.dom import minidom
from zipfile import ZipFile
import common_functions
from PIL import Image
import argparse
import shutil
import time
import os

# Setup constants for later use
whitelist =    ['red_power_port_high_goal', 'blue_power_port_high_goal', 'power_cell']
convert_list = ['Goal',                     'Goal',                      'Power_Cell']


def pascal2pascal():

    # Initialize parser
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool. Annotation manipulation program') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # String arguments
    required_args.add_argument("-i", "--input",  required = True, help = "Input path to the folder containing the data to be converted.")
    parser.add_argument(       "-o", "--output", required = True, help = "Output path for the converted data. All images will be copied here as well. If nothing is specified, then the .xmls in the input directory will be modifed.")

    # Optional (Boolean) arguments
    parser.add_argument("-c", "--cleanup",         action = "store_true", default = False, help = "If parameter is specified, then the input folder path will be automatically deleted after use")
    parser.add_argument("-f", "--feedback",        action = "store_true", default = True,  help = "If parameter is specified, then the feedback will be provided during the conversion process")
    parser.add_argument("-d", "--debug",           action = "store_true", default = False, help = "If parameter is specified, then the temporary folders will be left for examination")
    parser.add_argument("-p", "--prepare_dataset", action = "store_true", default = False, help = "If parameter is specified, then the files will also be copied into a dataset for training. Requires the output argument.")

    # Read arguments from command line 
    args = parser.parse_args()

    # Start timer
    start_time = time.time()
    
    # Get the full input path
    input_path = os.path.abspath(args.input)

    # If we have an output path
    if args.output is not None:

        # Get the full output path
        output_path = os.path.abspath(args.output)

        # Create the output folder if necessary
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
            
            # Provide feedback
            if args.feedback:
                print("Created output folder")

        else:
            # Provide feedback
            if args.feedback:
                print("Output folder exists, no need to create it")

        # Check delete the image folder if it exists
        if os.path.isdir(os.path.join(output_path, "JPEGImages")):
            shutil.rmtree(os.path.join(output_path, "JPEGImages"))

        # Check if the annotations folder exists, then delete
        if os.path.isdir(os.path.join(output_path, "Annotations")):
            shutil.rmtree(os.path.join(output_path, "Annotations"))

        # Create temporary folders
        os.mkdir(os.path.join(output_path, "JPEGImages"))
        os.mkdir(os.path.join(output_path, "Annotations"))

        # Read the input directory's files
        input_files = os.listdir(input_path)

        # Provide feedback
        if args.feedback:
            print("Copying files")

        # Create an accumulator
        current_file_index = 1

        # Copy them over
        for filename in input_files:

            # Get the file's extension
            raw_filename, file_ext = os.path.splitext(filename)

            # Copy the .xmls, then convert them
            if file_ext == ".xml":

                # If the specified, move the annotations to their folder for dataset creation
                if args.prepare_dataset:

                    # Copy the .xml annotation
                    shutil.copy(os.path.join(input_path, filename), os.path.join(output_path, "Annotations"))

                    # Convert the copied .xml
                    convert_xml_annotation(filename, os.path.join(output_path, "Annotations"), whitelist, convert_list, args.prepare_dataset)

                # Otherwise, just copy the files over to the output folder
                else:

                    # Copy the .xml annotation
                    shutil.copy(os.path.join(input_path, filename), output_path)

                    # Convert the copied .xml
                    convert_xml_annotation(filename, output_path, whitelist, convert_list, args.prepare_dataset)


            # Copy the .jpgs
            elif file_ext == ".jpg":
                if args.prepare_dataset:
                    shutil.copy(os.path.join(input_path, filename), os.path.join(output_path, "JPEGImages"))
                else:
                    shutil.copy(os.path.join(input_path, filename), output_path)

            # Copy the other files, such as photos
            elif file_ext == ".png" or file_ext == ".JPG":

                # Open the image
                image = Image.open(os.path.join(input_path, filename))

                # Create the new filename
                new_filename = raw_filename + '.jpg'

                # Save the image to the dataset folder if specified, otherwise just to the output folder
                if args.prepare_dataset:
                    image.save(os.path.join(output_path, "JPEGImages", new_filename))
                else:
                    image.save(os.path.join(output_path, new_filename))


            # Provide feedback
            if args.feedback:
                print("Current file index: " + str(current_file_index) + " out of " + str(len(input_files)))

            # Increment the counter
            current_file_index = current_file_index + 1

        # Clean up the folder if specified
        if args.cleanup:
            shutil.rmtree(input_path)

        # Zip the dataset up if specified
        if args.prepare_dataset:
            common_functions.zip_dataset(output_path, "dataset", args.debug)

    # Just modify the input folder's .xmls
    else:

        # You can't have a dataset generated without an output folder
        if args.prepare_dataset:
            raise AttributeError('A dataset cannot be prepared if no output is specified.')

        # We're good, continue with the modification
        else:

            # Get the list of files in the input directory
            input_files = os.listdir(input_path)

            # Provide feedback
            if args.feedback:
                print("Modifying files")

            # Create a counter
            current_file_index = 1

            # Copy them over
            for filename in input_files:

                # Get the file's extension
                raw_filename, file_ext = os.path.splitext(filename)

                # Convert the .xml file 
                if file_ext == ".xml":
                    convert_xml_annotation(filename, output_path, whitelist, convert_list, args.prepare_dataset)

                # Copy the other files, such as photos
                elif file_ext == ".png" or file_ext == ".JPG":

                    # Open the image
                    image = Image.open(os.path.join(input_path, filename))

                    # Create the new filename
                    new_filename = raw_filename + '.jpg'

                    # Save the image
                    image.save(os.path.join(input_path, new_filename))

                    # Remove the .png
                    os.remove(os.path.join(input_path, filename))

                # Provide feedback
                if args.feedback:
                    print("Current file index: " + str(current_file_index) + " out of " + str(len(input_files)))

                # Increment the counter
                current_file_index = current_file_index + 1

    # End the counter, the operation has completed
    end_time = time.time()

    # Calculate the time taken
    time_taken = end_time - start_time

    # Print out time if feedback is enabled
    if args.feedback:
        print("Conversion process took " + str(round(time_taken, 2)) + " seconds")



# Function for converting the .xmls
def convert_xml_annotation(filename, filepath, whitelist, convert_list, prepare_dataset):

    # Accumulator for later deletions
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
        tree.write(os.path.join(filepath, filename))


pascal2pascal()