# Written by Christian Piper and William Corvino
# First Robotics Team 834
# Created: 8/23/20

# Gets all of the file paths in a directory, then returns a list of paths
from ndjson.api import writer


def get_all_file_paths(directory):

    # Import necessary libaries
    import os
  
    # Create empty file paths list 
    file_paths = []
  
    # Get all of the files in the directory
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
  
    # Return all file paths 
    return file_paths


# Builds a PascalVOC annotation from an object array, the name of the image, and the output folder
def build_PascalVOC_annotation(objects, image_name, output_folder):

    # Import libaries
    import xml.etree.ElementTree as xml
    from PIL import Image
    import os

    # Check to see if we have any labels, if not, then don't do anything
    if objects:

        # Get the file's name for splitting
        raw_image_name, file_ext = os.path.splitext(image_name)

        # Create master annotation element
        annotation = xml.Element('annotation')

        # Get folder name (not important)
        folder = xml.SubElement(annotation, 'folder')
        folder.text = os.path.basename( os.path.join(output_folder, "JPEGImages") )

        # Filename
        filename = xml.SubElement(annotation, 'filename')
        filename.text = image_name

        # Path 
        path = xml.SubElement(annotation, 'path')
        path.text = os.path.join(output_folder, "JPEGImages", image_name)

        # Database (not important)
        source = xml.SubElement(annotation, 'source')
        database = xml.SubElement(source, 'database')
        database.text = "None"

        # Open the image to get parameters from it
        image = Image.open(os.path.join(output_folder, "JPEGImages", image_name))
        image_width, image_height = image.size

        # Image size parameters
        size = xml.SubElement(annotation, 'size')
        width = xml.SubElement(size, 'width')
        width.text = str(image_width)
        height = xml.SubElement(size, 'height')
        height.text = str(image_height)

        # Depth is 3 for color, 1 for black and white
        depth = xml.SubElement(size, 'depth')
        depth.text = str(3)

        # Segmented (not important)
        segmented = xml.SubElement(annotation, 'segmented')
        segmented.text = str(0)
    
        # Objects... where the fun begins
        for object_list in objects:
            # Declare an object
            object_ = xml.SubElement(annotation, 'object')

            # Name
            name = xml.SubElement(object_, 'name')
            name.text = object_list[0]

            # Bounding box
            bounding_box = xml.SubElement(object_, 'bndbox')
            x_min = xml.SubElement(bounding_box, 'xmin')
            y_min = xml.SubElement(bounding_box, 'ymin')
            x_max = xml.SubElement(bounding_box, 'xmax')
            y_max = xml.SubElement(bounding_box, 'ymax')
            x_min.text = str(object_list[1])
            y_min.text = str(object_list[2])
            x_max.text = str(object_list[3])
            y_max.text = str(object_list[4])
        
        with open(os.path.join(output_folder, "Annotations", (raw_image_name + '.xml')), 'w') as xml_file:
            xml_file.write(prettify_xml(annotation))
            xml_file.close()


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element.
    """

    # Import libaries
    from xml.etree import ElementTree
    from xml.dom import minidom

    # Convert the XML to a string
    rough_string = ElementTree.tostring(elem, 'utf-8')

    # Load the XML string
    reparsed = minidom.parseString(rough_string)

    # Add spacing to string to fix formatting, then return it
    return reparsed.toprettyxml(indent="  ")

# Zips a PascalVOC datset up for uploading and downloading
def zip_dataset(output_path, zip_filename, debug):

    # Import libaries
    from zipfile import ZipFile
    import shutil
    import os

    # Find all of the converted files and folders
    image_file_paths = get_all_file_paths(os.path.join(output_path, "JPEGImages"))
    annotation_file_paths = get_all_file_paths(os.path.join(output_path, "Annotations"))

    # Write each of the files to a zip
    file_name = os.path.join(output_path, zip_filename + ".zip")
    with ZipFile(file_name, 'w') as zip_file: 

        # Write each image 
        for file_ in image_file_paths: 
            zip_file.write(file_, arcname = os.path.join("JPEGImages", os.path.basename(file_)))

        # Write each annotation
        for file_ in annotation_file_paths: 
            zip_file.write(file_, arcname = os.path.join("Annotations", os.path.basename(file_)))

    # Clean up the output of temporary folders
    if not debug:
        shutil.rmtree(os.path.join(output_path, "JPEGImages"))
        shutil.rmtree(os.path.join(output_path, "Annotations"))


# Flips the input image horizontally. Takes in the filename (in the input folder) and the input and folders
def flip_image(filename, input_folder_path, output_folder_path):

    # Import requirements
    from PIL import Image, ImageOps
    import os

    # Get the file's name for splitting
    raw_filename, file_ext = os.path.splitext(filename)
    
    # Get the annotation data from the respective annotation file
    image_objects = get_Supervisely_objects(filename, input_folder_path)

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
        build_PascalVOC_annotation(image_objects, new_filename, output_folder_path)


# Gets all of the objects in a Supervisely annotation
def get_Supervisely_objects(image_name, input_supervisely_folder):

    # Import libraries
    import json
    import os

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


# Crops an image using the filename (in input folder), the output, and the allowed crop percentages. It also has a safety of a minimum percentage of original size
def crop_image(filename, input_folder_path, output_folder_path, allowed_percent_crop_lower, allowed_percent_crop_upper, minimum_box_percent):

    # Import libraries
    from PIL import Image
    from random import randint
    import os

    # Get the file's name for splitting
    raw_filename, file_ext = os.path.splitext(filename)

    # Get the annotation data from the respective annotation file
    image_objects = get_Supervisely_objects(filename, input_folder_path)

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
        build_PascalVOC_annotation(image_objects, new_filename, output_folder_path)


# Adds Gaussian (basically random) noise to an image with the image's name (must be in the input folder), input folder, and output folder
def gaussian_noise_image(filename, input_folder_path, output_folder_path):

    # Import libraries
    from skimage.util import random_noise
    from PIL import Image
    import numpy as np
    import os

    # Get the file's name for splitting
    raw_filename, file_ext = os.path.splitext(filename)
    
    # Get the annotation data from the respective annotation file
    image_objects = get_Supervisely_objects(filename, input_folder_path)

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
        build_PascalVOC_annotation(image_objects, new_filename, output_folder_path)


# Extracts the data from a PascalVOC .xml file into an object list
def get_PascalVOC_objects(filename, input_path):

    # Import libraries
    from xml.etree import ElementTree
    import os

    # Create object accumulator
    object_list = []

    # Get the file's extension
    raw_filename, file_ext = os.path.splitext(filename)

    # Copy the .xmls, then convert them
    if file_ext != ".xml":

        # Throw error
        print("File specified is not an xml!")
        return -1

    # Open the file with the element tree
    tree = ElementTree.parse(os.path.join(input_path, filename))

    # Get the root of the XML
    root = tree.getroot()

    # Loop through to find the parameters that need to be changed
    for possible_object in root:

        # Check for the objects in a file
        if possible_object.tag == 'object':

            # Create an array that will be appended to the object list later
            object = ["", 0, 0, 0, 0]

            # We found an object!
            for object_parameter in possible_object:

                # Get to the names of the objects
                if object_parameter.tag == 'name':

                    # Add the object's name to the first element of the array
                    object[0] = object_parameter.text

                # Get the object's bounding box values
                elif object_parameter.tag == 'bndbox':

                    # Cycle through the values in the bounding box
                    for value in object_parameter:

                        # Check to see what the value is, then set the respective value in the object array
                        if value.tag == 'xmin':
                            object[1] = int(value.text)

                        if value.tag == 'ymin':
                            object[2] = int(value.text)

                        if value.tag == 'xmax':
                            object[3] = int(value.text)

                        if value.tag == 'ymax':
                            object[4] = int(value.text)

            # We finished the loop, time to add the object that we made to the main array
            object_list.append(object)

    # Return the array we created
    return object_list


# Builds a ndjson annotation from an object list
def build_ndjson_annotation(object_list, annotation_name, output_folder):

    # Import libraries
    import ndjson
    import os

    # Get the raw filename
    raw_annotation_name, annotation_ext = os.path.splitext(annotation_name)
    
    # Open a new file for writing
    with open(os.path.join(output_folder, raw_annotation_name + ".ndjson"), "w+") as ndjson_file:
        
        # Open the file writer
        ndjson_writer = ndjson.writer(ndjson_file, ensure_ascii = False)
        
        # Loop through each of the objects in the object list
        for object_ in object_list:

            # Create a dictionary with the object's array
            object_dict = {"uuid":      "141", 
                            "schemaId": "141", 
                            "dataRow":  {
                                "id": "141"
                            },
                            "bbox": {
                                "top":    object_[1],
                                "left":   object_[2],
                                "height": object_[3] - object_[1],
                                "width":  object_[4] - object_[2]
                            }} 

            # Write the dictionary to a new row 
            ndjson_writer.writerow(object_dict)

        # Close the file
        ndjson_file.close()

# Function to read a ndjson into an object list
def get_ndjson_objects(filename, input_path):

    # Import the libraries
    import ndjson
    import os
    
    # Open the file
    with open(os.path.join(input_path, filename + ".ndjson"), "w+") as ndjson_file:

        # Create a reader for the file
        ndjson_reader = ndjson.reader(ndjson_file)