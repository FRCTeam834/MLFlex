# Import libraries
import xml.etree.ElementTree as xml
from xml.etree import ElementTree
from xml.dom import minidom
import argparse
import glob
import os

# Setup constants for later use
whitelist =    ['red_robot', 'blue_robot', 'red_power_port_high_goal', 'blue_power_port_high_goal', 'power_cell', 'color_wheel']
convert_list = ['Red_Robot', 'Blue_Robot', 'Goal',                     'Goal',                      'Power_Cell', 'Color_Wheel']

'''
def main():

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
    parser.add_argument("-a", "--augmentation", action = "store_true", default = True,  help = "If parameter is specified, then additional flipped and cropped versions of the images and annotations will be included in the output")
    
    # Read arguments from command line 
    args = parser.parse_args()
    
    # Get the full paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    # Find out what Supervisely folders are available
    subfolders = [ f.path for f in os.scandir(input_path) if f.is_dir() ]

    # Now run through with the valid folders
    current_folder_index = 0
    for folder in subfolders:
        # Print feedback
        if args.feedback:
            print()
            print("Converting " + os.path.basename(folder))


        # Convert
        if args.join:
            convert_Supervisely_2_Pascal_VOC(os.path.abspath(folder), output_path, args.cleanup, args.feedback, args.augmentation, args.augmentation, args.augmentation, last_folder, debug = args.debug)
        else:
            convert_Supervisely_2_Pascal_VOC(os.path.abspath(folder), output_path, args.cleanup, args.feedback, args.augmentation, args.augmentation, args.augmentation, True, debug = args.debug)

        # Increment the counter
        current_folder_index = current_folder_index + 1
'''

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


convert_xml_annotation('example_xml.xml', os.path.abspath('C:\\Users\\Staack\\Desktop\\Christian\\Robotics'), whitelist, convert_list)