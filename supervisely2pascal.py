# Written by Christian Piper and William Corvino
# First Robotics Team 834
# Created: 7/2/20
# Last updated: 12/22/20

# Import libraries
from skimage.util import random_noise
from PIL import Image, ImageOps
import common_functions
import argparse
import shutil
import time
import glob
import os

# Setup constants for later use
supported_formats = '.jpg', '.JPG', '.png', '.PNG' # .............................. Specifies the allowable image formats
allowed_percent_crop_lower = 1 # .................................................. Specifies the smallest allowable crop percentage
allowed_percent_crop_upper = 5 # .................................................. Specifies the largest allowable crop percentage
minimum_box_percent = 2 # ......................................................... Specifies the smallest allowable size of a box in percent of image dimension


def supervisely2pascal():

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

    # Provide feedback
    if args.feedback:
        print("Creating output folder structure")

    # Check delete the image folder if it exists
    if os.path.isdir(os.path.join(output_path, "JPEGImages")):
        shutil.rmtree(os.path.join(output_path, "JPEGImages"))
    
    # Check if the annotations folder exists, then delete
    if os.path.isdir(os.path.join(output_path, "Annotations")):
        shutil.rmtree(os.path.join(output_path, "Annotations"))

    # Create temporary folders
    os.mkdir(os.path.join(output_path, "JPEGImages"))
    os.mkdir(os.path.join(output_path, "Annotations"))

    # Find out what Supervisely folders are available
    subfolders = [ f.path for f in os.scandir(input_path) if f.is_dir() ]

    # Verify the folders are valid
    current_folder_index = 0
    for folder in subfolders:
        # Format the path to the expected version
        folder = os.path.abspath(folder)

        # Check if the annotations folder exists, which would mean it is a Supervisely folder
        if not os.path.isdir(os.path.join(os.path.abspath(folder), "ann")):
            # This isn't a Supervisely folder, remove it
            subfolders.pop(current_folder_index)
            if args.feedback:
                print(os.path.basename(folder) + " was not a valid folder")
                print(os.path.join(os.path.abspath(folder), "ann"))


        # Increment the counter
        current_folder_index = current_folder_index + 1

    # Now run through with the valid folders
    current_folder_index = 0
    for folder in subfolders:
        # Print feedback
        if args.feedback:
            print()
            print("Converting " + os.path.basename(folder))

        # Check if this is the last folder, that way the function will zip everything at the end
        if current_folder_index == (len(subfolders) - 1):
            last_folder = True
        else:
            last_folder = False


        # Convert
        if args.join:
            convert_Supervisely_2_Pascal_VOC(os.path.abspath(folder), output_path, args.cleanup, args.feedback, args.augmentation, args.augmentation, args.augmentation, last_folder, debug = args.debug)
        else:
            convert_Supervisely_2_Pascal_VOC(os.path.abspath(folder), output_path, args.cleanup, args.feedback, args.augmentation, args.augmentation, args.augmentation, True, debug = args.debug)

        # Increment the counter
        current_folder_index = current_folder_index + 1


def convert_Supervisely_2_Pascal_VOC(input_supervisely_folder, output_folder, cleanup, feedback, flipped_images, cropped_images, include_gaussian_noise_images, create_zip, debug = False):
    """
    Converts a folder of Supervisely annotations to PascalVOC format 

    :param input_supervisely_folder: The folder of Supervisely annotations and images for conversion
    :param output_folder: The folder for the final zip file
    :param cleanup: Should the Supervisely folder be deleted
    :param feedback: Provides feedback on the conversion process
    :param flipped_images: Adds flipped versions of the images to the output
    :param cropped_images: Adds cropped versions of the images to the output
    :param gaussian_noise_images: Adds Gaussian noise versions of the images to the output
    :param create_zip: Creates a zip file of the data and cleans up the temporary folders. If false, folders will remain untouched
    :param debug: Doesn't delete the output folders
    """

    # Take note of the start time
    start_time = time.time()

    # Make sure the temporary folders are in place
    if not os.path.isdir(os.path.join(output_folder, "JPEGImages")):
        os.mkdir(os.path.join(output_folder, "JPEGImages"))

    if not os.path.isdir(os.path.join(output_folder, "Annotations")):
        os.mkdir(os.path.join(output_folder, "Annotations"))

    # Provide feedback
    if feedback:
        print("Beginning counting available images")

    # Create an empty accumulator for a readout of the progress
    image_name_list = []

    # Get all of the files in the input directory
    for filename in os.listdir(os.path.join(input_supervisely_folder, 'img')):

        # Make sure that each file is an image
        for image_format in supported_formats:

            # Check if the image format is an image
            if filename.endswith(image_format):
                image_name_list.append(filename)

    # Give feedback on current process
    if feedback:
        print("Starting conversion process for " + str(len(image_name_list)) + " images")

    # Declare counter and begin the conversion process
    current_image_index = 0
    for image_name in image_name_list:

        # Convert the original image
        convert_original_image(image_name, input_supervisely_folder, output_folder)

        # Flip the image
        if flipped_images:
            common_functions.flip_image(image_name, input_supervisely_folder, output_folder)

        # Crop the images
        if cropped_images:
            common_functions.crop_image(image_name, input_supervisely_folder, output_folder, allowed_percent_crop_lower, allowed_percent_crop_upper, minimum_box_percent)

        # Add noise to images
        if include_gaussian_noise_images:
            common_functions.gaussian_noise_image(image_name, input_supervisely_folder, output_folder)

        # Count that this image is finished
        current_image_index = current_image_index + 1

        # Print the progress
        if feedback:
            print("Progress: " + str(current_image_index) + "/" + str(len(image_name_list)))

    # If specified, convert the object name, then zip the files into a dataset
    if create_zip:

        # Get the project name, then replace the spaces with underscores
        supervisely_project_name = os.path.basename(input_supervisely_folder)
        formatted_name = supervisely_project_name.replace(" ", "_")

        # Zip the files into a dataset
        common_functions.zip_dataset(output_folder, formatted_name, debug)

    # Clean up the Supervisely folder as well if indicated
    if cleanup:

        # Need to delete the input folder
        shutil.rmtree(input_supervisely_folder)

    # Record the ending time
    end_time = time.time()

    # Provide feedback
    if feedback:
        print("Finished converting " + str(len(image_name_list)) + " images")
        print("Conversion time: " + str(round(end_time - start_time, 2)) + " seconds")


def convert_original_image(filename, input_folder_path, output_folder_path):
    
    # Get annotation data from the respective annotation file
    image_objects = common_functions.get_Supervisely_objects(filename, input_folder_path)

    # Check if the image has valid data. If not, it can't be used
    if image_objects:

        # Get the file's name for splitting
        raw_filename, file_ext = os.path.splitext(filename)
        
        # Create an image for copying
        image = Image.open(os.path.join(input_folder_path, 'img', filename))
        
        # Save the output image to the specified directory
        new_filename = os.path.basename(input_folder_path) + "_" + raw_filename
        new_filename = new_filename.replace(" ", "_")
        image.save(os.path.join(output_folder_path, "JPEGImages", (new_filename + ".jpg")))

        # Build an xml with the old file
        common_functions.build_xml_annotation(image_objects, (new_filename + ".jpg"), output_folder_path)





supervisely2pascal()