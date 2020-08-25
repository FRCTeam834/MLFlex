# Written by Christian Piper and William Corvino
# First Robotics Team 834
# Created: 7/2/20

# Import libraries
from skimage.util import random_noise
from PIL import Image, ImageOps
import common_functions
from zipfile import ZipFile
from random import randint
import numpy as np
import argparse
import shutil
import time
import json
import glob
import os

# Setup constants for later use
supported_formats = '.jpg', '.JPG', '.png', '.PNG' # .............................. Specifies the allowable image formats
allowed_percent_crop_lower = 1 # .................................................. Specifies the smallest allowable crop percentage
allowed_percent_crop_upper = 5 # .................................................. Specifies the largest allowable crop percentage
minimum_box_percent = 2 # ......................................................... Specifies the smallest allowable size of a box in percent of image dimension


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
    """Converts a folder of Supervisely annotations to PascalVOC format 

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
            flip_image(image_name, input_supervisely_folder, output_folder)

        # Crop the images
        if cropped_images:
            crop_image(image_name, input_supervisely_folder, output_folder, allowed_percent_crop_lower, allowed_percent_crop_upper, minimum_box_percent)

        # Add noise to images
        if include_gaussian_noise_images:
            gaussian_noise_image(image_name, input_supervisely_folder, output_folder)

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
    image_objects = get_image_objects(filename, input_folder_path)

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


def flip_image(filename, input_folder_path, output_folder_path):

    # Get the file's name for splitting
    raw_filename, file_ext = os.path.splitext(filename)
    
    # Get the annotation data from the respective annotation file
    image_objects = get_image_objects(filename, input_folder_path)

    # Check if the image has valid data. If not, it can't be used
    if image_objects:

        # Create an image for manipulation
        image = Image.open(os.path.join(input_folder_path, 'img/', filename))

        # Flip the image
        flipped_image = ImageOps.mirror(image)

        image_width, image_height = flipped_image.size

        # Save the output image to the specified directory
        new_filename = os.path.basename(input_folder_path) + "_" + raw_filename + "_flipped.jpg"
        new_filename = new_filename.replace(" ", "_")
        flipped_image.save(os.path.join(output_folder_path, "JPEGImages", new_filename))

        # Apply adjustments
        for object_ in image_objects:
            # Flip only the X coords, not the Ys
            x_min_offset = image_width - object_[1]
            x_max_offset = image_width - object_[3]
            object_[1] = x_max_offset
            object_[3] = x_min_offset

        # Save a new xml file for the annotation data
        common_functions.build_xml_annotation(image_objects, new_filename, output_folder_path)


def get_image_objects(image_name, input_supervisely_folder):

    # Create a accumulator
    objects = []

    # Set up and open the json annotation file
    with open(os.path.join(input_supervisely_folder, 'ann', (image_name + '.json'))) as annotation_file:
        annotations = json.load(annotation_file)

    # For each of the objects in the annotation file, add a listing to the accumulator
    for object_ in annotations["objects"]:
        # Grab the name of the object
        object_name = object_["classTitle"]

        # Navigate to the correct level of the dictionary and grab the point data
        points = object_["points"]
        exterior_points = points["exterior"]
        left, upper = exterior_points[0]
        right, lower = exterior_points[1]

        # Add the object to the list of objects
        objects.append([object_name, left, upper, right, lower])

    return objects 


def crop_image(filename, input_folder_path, output_folder_path, allowed_percent_crop_lower, allowed_percent_crop_upper, minimum_box_percent):

    # Get the file's name for splitting
    raw_filename, file_ext = os.path.splitext(filename)

    # Get the annotation data from the respective annotation file
    image_objects = get_image_objects(filename, input_folder_path)

    # Check if the image has valid data. If not, it can't be used
    if image_objects:

        # Create an image for manipulation
        image = Image.open(os.path.join(input_folder_path, 'img/', filename))

        # Get the bounding box of the image
        (left, upper, right, lower) = image.getbbox()

        # Get random values for the adjustment by getting a random percent
        left_adjust = right * (randint(allowed_percent_crop_lower, allowed_percent_crop_upper) / 100)
        upper_adjust = lower * (randint(allowed_percent_crop_lower, allowed_percent_crop_upper) / 100)
        right_adjust = right * (randint(allowed_percent_crop_lower, allowed_percent_crop_upper) / 100)
        lower_adjust = lower * (randint(allowed_percent_crop_lower, allowed_percent_crop_upper) / 100)

        # Adjust the coordinates for the changes
        left = left + left_adjust
        upper = upper + upper_adjust
        right = right - right_adjust
        lower = lower - lower_adjust

        # Crop the image to the specified size
        cropped_image = image.crop((left, upper, right, lower))

        # Get the size of the image for sanity checking
        cropped_image_width, cropped_image_height = cropped_image.size

        # Save the output image to the specified directory
        new_filename = os.path.basename(input_folder_path) + "_" + raw_filename + "_cropped.jpg"
        new_filename = new_filename.replace(" ", "_")
        cropped_image.save(os.path.join(output_folder_path, "JPEGImages", new_filename))

        # Apply adjustments
        current_object = 0
        for object_ in image_objects:

            # Create a check that will delete the object if it is no longer on screen
            invalid_coordinates = False

            # Cycle through the coordinates, adjusting and checking each one
            for coordinate_num in range(1, 5):

                if (coordinate_num % 2) == 0:
                    # Number is even, and is a Y coordinate
                    object_[coordinate_num] = object_[coordinate_num] - upper_adjust

                else:
                    # Number is odd, is an X coordinate
                    object_[coordinate_num] = object_[coordinate_num] - left_adjust


            # Sanity checking to make sure the the coords are still valid
            # Check to see if the coordinate is out of bounds

            # X
            # Right side checking
            if object_[1] > cropped_image_width:

                # Whole box is out of range to the right
                invalid_coordinates = True

            elif object_[3] > cropped_image_width:

                # Only the right of the box is out of range, we can just move the right coord to meet the right side of the image
                object_[3] = cropped_image_width

                # Make sure that the adjusted box isn't too small
                box_width = object_[3] - object_[1]
                smallest_allowable_width = cropped_image_width * (minimum_box_percent / 100)

                if box_width < smallest_allowable_width:

                    # Box is too small
                    invalid_coordinates = True

            # Left side checking
            elif object_[3] < 0:

                # Whole box is out of range to the left
                invalid_coordinates = True

            elif object_[1] < 0:

                # Only the left of the box is out of range, we can just move the left coord to meet the left side of the image
                object_[3] = cropped_image_width
                
                # Make sure that the adjusted box isn't too small
                box_width = object_[3] - object_[1]
                smallest_allowable_width = cropped_image_width * (minimum_box_percent / 100)

                if box_width < smallest_allowable_width:

                    # Box is too small
                    invalid_coordinates = True

            # Y
            # Bottom checking
            if object_[2] > cropped_image_height:

                # Whole box is out of range
                invalid_coordinates = True

            elif object_[4] > cropped_image_height:

                # Only the bottom of the box is out of range, we can just move the lower coord to meet the bottom of the image
                object_[4] = cropped_image_height

                # Make sure that the box isn't too small
                box_height = object_[4] - object_[2]
                smallest_allowable_height = cropped_image_height * (minimum_box_percent / 100)

                if box_height < smallest_allowable_height:
                    # Box is too small
                    invalid_coordinates = True

            # Top checking
            elif object_[4] < 0:

                # Whole box is out of range
                invalid_coordinates = True

            elif object_[2] < 0:

                # Only the top of the box is out of range, we can just move the upper coord to meet the top of the image
                object_[2] = cropped_image_height

                # Make sure that the box isn't too small
                box_height = object_[4] - object_[2]
                smallest_allowable_height = cropped_image_height * (minimum_box_percent / 100)

                if box_height < smallest_allowable_height:

                    # Box is too small
                    invalid_coordinates = True

            # Delete the coordinate if it is invalid
            if invalid_coordinates:
                image_objects.pop(current_object)
            
            # Continue to count the current object
            current_object = current_object + 1

        # Save a new xml file for the annotation data
        common_functions.build_xml_annotation(image_objects, new_filename, output_folder_path)


def gaussian_noise_image(filename, input_folder_path, output_folder_path):

    # Get the file's name for splitting
    raw_filename, file_ext = os.path.splitext(filename)
    
    # Get the annotation data from the respective annotation file
    image_objects = get_image_objects(filename, input_folder_path)

    # Check if the image has valid data. If not, it can't be used
    if image_objects:

        # Create an image for manipulation
        image = Image.open(os.path.join(input_folder_path, 'img/', filename))

        # Convert the image to an array for manipulation
        image_array = np.asarray(image)

        # random_noise() method will convert image in [0, 255] to [0, 1.0],
        # inherently it use np.random.normal() to create normal distribution
        # and adds the generated noised back to image
        noise_img = random_noise(image_array, mode = 'gaussian', var = 0.05**2)
        noise_img = (255 * noise_img).astype(np.uint8)

        gaussian_noise_image = Image.fromarray(noise_img)

        # Save the output image to the specified directory
        new_filename = os.path.basename(input_folder_path) + "_" + raw_filename + "_gaussian_noise.jpg"
        new_filename = new_filename.replace(" ", "_")
        gaussian_noise_image.save(os.path.join(output_folder_path, "JPEGImages", new_filename))

        # Save a new xml file for the annotation data
        common_functions.build_xml_annotation(image_objects, new_filename, output_folder_path)


main()