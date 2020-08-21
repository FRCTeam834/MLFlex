# Import libraries
import xml.etree.ElementTree as xml
from xml.etree import ElementTree
from xml.dom import minidom
from PIL import Image
import argparse
import shutil
import os

# Setup constants for later use
whitelist =    ['red_robot', 'blue_robot', 'red_power_port_high_goal', 'blue_power_port_high_goal', 'power_cell', 'color_wheel']
convert_list = ['Red_Robot', 'Blue_Robot', 'Goal',                     'Goal',                      'Power_Cell', 'Color_Wheel']


def main():

    # Initialize parser 
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool. Annotation manipulation program') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # String arguments
    required_args.add_argument("-i", "--input",  required = True, help = "Input path to the folder containing the data to be converted.")
    parser.add_argument("-o", "--output", required = True, help = "Output path for the converted data. All images will be copied here as well. If nothing is specified, then the .xmls in the input directory will be modifed.")

    # Optional (Boolean) arguments
    parser.add_argument("-c", "--cleanup",      action = "store_true", default = False, help = "If parameter is specified, then the input folder path will be automatically deleted after use")
    parser.add_argument("-f", "--feedback",     action = "store_true", default = True,  help = "If parameter is specified, then the feedback will be provided during the conversion process")
    
    # Read arguments from command line 
    args = parser.parse_args()
    
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

        # Read the input directory's files
        input_files = os.listdir(input_path)

        # Provide feedback
        if args.feedback:
            print("Copying files")

        # Create an accumulator
        current_file_index = 0

        # Copy them over
        for filename in input_files:

            # Get the file's extension
            raw_filename, file_ext = os.path.splitext(filename)

            # Copy the .xmls, then convert them
            if file_ext == ".xml":
                shutil.copy(os.path.join(input_path, filename), output_path)

                # Convert the copied .xml
                convert_xml_annotation(filename, output_path, whitelist, convert_list)

            # Copy the .jpgs
            elif file_ext == ".jpg":
                shutil.copy(os.path.join(input_path, filename), output_path)

            # Copy the other files, such as photos
            elif file_ext == ".png":

                # Open the image
                image = Image.open(os.path.join(input_path, filename))

                # Create the new filename
                new_filename = raw_filename + '.jpg'

                # Save the image
                image.save(os.path.join(output_path, new_filename))

            # Provide feedback
            if args.feedback:
                print("Current file index: " + str(current_file_index) + "//" + str(len(input_files)))

            # Increment the counter
            current_file_index = current_file_index + 1

        # Clean up the folder if specified
        if args.cleanup:
            shutil.rmtree(input_path)

    # Just modify the input folder's .xmls
    else:
        
        # Get the list of files in the input directory
        input_files = os.listdir(input_path)

        # Provide feedback
        if args.feedback:
            print("Modifying files")

        # Create an accumulator
        current_file_index = 0

        # Copy them over
        for filename in input_files:

            # Get the file's extension
            raw_filename, file_ext = os.path.splitext(filename)

            # Convert the .xml file 
            if file_ext == ".xml":
                convert_xml_annotation(filename, output_path, whitelist, convert_list)

            # Copy the other files, such as photos
            elif file_ext == ".png":

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
                print("Current file index: " + str(current_file_index) + "/" + str(len(input_files)))

            # Increment the counter
            current_file_index = current_file_index + 1



# Function for converting the .xmls
def convert_xml_annotation(filename, filepath, whitelist, convert_list):

    # Accumulator for later deletions
    invalid_objects = []
    
    # Get the structure of the XML
    tree = ElementTree.parse(os.path.join(filepath, filename))

    # Get the root of the XML
    root = tree.getroot()

    for possible_object in root:
        # Check the objects in a file

        if possible_object.tag == 'object':
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
                        print("Removing: " + str(possible_object))
                        print("Name: " + possible_object.tag)
                        print("Object name: " + possible_object.getchildren()[0].text)
                        invalid_objects.append(possible_object)
                        
    # Remove the invalid object
    for invalid_object in invalid_objects:
        root.remove(invalid_object)

    # Remove the old XML
    os.remove(os.path.join(filepath, filename))
    
    # Write out the new file
    tree.write(os.path.join(filepath, filename))


main()