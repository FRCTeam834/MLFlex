# Written by Christian Piper and Mohammad Durrani
# FRC Team 834
# Created: 12/26/20

# Import libraries
import common_functions
import argparse
import ndjson
import shutil
import time
import os

def ndjson2pascal():
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
    os.mkdir(os.path.join(output_path, "JPEGImages"))
    filepath = os.path.join(output_path, "Annotations")

    # Get the files in the input folder
    input_files = os.listdir(input_path)

    # Set the file index if we're providing feedback
    if args.feedback:
        current_file_index = 1
    
    # Loop through all of the files
    for filename in input_files:

        # Get the list of objects in an image
        image_objects = common_functions.get_ndjson_objects(filename, input_path)
        
        # Build a PascalVOC annotation from the list of objects
        common_functions.build_PascalVOC_annotation(image_objects, filename, os.path.join(output_path, "Annotations"))

        # Print feedback if the user wants it
        if args.feedback:

            # Print the index of the file out of the total
            print("Current file: " + str(current_file_index) + " out of " + str(len(input_files)))
            
            # Increment the counter
            current_file_index =+ 1

    # Cleanup the input path if specified
    if args.cleanup:
        shutil.rmtree(input_path)
    
    # Calculate total time to run
    total_time = time.time()-start_time

    # Print conversion time
    if args.feedback: 
        print("Total time to convert: " + str(round(total_time, 4) + " seconds"))

# Run the function
ndjson2pascal()