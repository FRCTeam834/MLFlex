# Written by Christian Piper
# First Robotics Team 834
# Created: 8/23/20

# Import libraries
import common_functions
from PIL import Image
import argparse
import random
import shutil
import time
import os

# Resources folder for available objects
objects_folder = "./resources/synthetic_objects"
image_objects_to_object_names = [["ball.jpg", "Power_Cell"], ["ball2.jpg", "Power_Cell"], ["ball3.jpg", "Power_Cell"]]
object_count_min = 1
object_count_max = 5
acceptable_file_extensions = [".jpg", ".JPG", ".png", ".PNG"]

def main():

    # Initialize parser 
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool. Annotation manipulation program') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # String arguments
    required_args.add_argument("-i", "--input",  required = True, help = "Input path to the folder containing the data to be converted.")
    required_args.add_argument("-o", "--output", required = True, help = "Output path for the converted data. All images will be copied here as well. If nothing is specified, then the .xmls in the input directory will be modifed.")

    # Optional (Boolean) arguments
    parser.add_argument("-c", "--cleanup",         action = "store_true", default = False, help = "If parameter is specified, then the input folder path will be automatically deleted after use")
    parser.add_argument("-f", "--feedback",        action = "store_true", default = True,  help = "If parameter is specified, then the feedback will be provided during the conversion process")
    parser.add_argument("-d", "--debug",           action = "store_true", default = False, help = "If parameter is specified, then the temporary folders will be left for examination")

    # Read arguments from command line 
    args = parser.parse_args()

    # Start timer
    start_time = time.time()
    
    # Get the full input path
    input_path = os.path.abspath(args.input)

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

        # Get the file extension
        raw_filename, file_ext = os.path.splitext(filename)

        # Check to see if the file extension is on the list. If so, create the synthetic training data
        for acceptable_file_ext in acceptable_file_extensions:
            if file_ext == acceptable_file_ext:

                # Create the data
                create_synthetic_image(filename, input_path, output_path, random.randint(object_count_min, object_count_max))
        
        # Provide feedback
        if args.feedback:
            print("Current file index: " + str(current_file_index) + " out of " + str(len(input_files)))

        # Increment the counter
        current_file_index = current_file_index + 1

    # Clean up the folder if specified
    if args.cleanup:
        shutil.rmtree(input_path)

    # Zip the dataset
    common_functions.zip_dataset(output_path, "dataset", args.debug)


def create_synthetic_image(input_image_filename, input_path, output_path, object_count):

    # Create an accumulator for the objects to be written to the annotation file
    image_objects = []

    # Open the image for modification
    image = Image.open(os.path.join(input_path, input_image_filename))

    # Get the size of the image
    image_width, image_height = image.size

    # Loop through to place objects in the frame
    for object_index in range(object_count):
        
        # Pick a random object to put into the frame. If it isn't in the list, pick another image
        while True:
            
            # Pick random object image
            object_image_filename = random.choice(os.listdir(objects_folder))

            # Create a boolean tracker
            valid_image = False

            # Go through the conversion list, checking to see if the filename is there
            for conversion_pair in image_objects_to_object_names:

                # Check to see it the filename matches the current conversion pair's
                if object_image_filename == conversion_pair[0]:
                    
                    # We have a match, meaning it's on the list
                    valid_image = True

                    # End the for loop
                    break

            # Now check the valid_image. If not, we need another loop to find another valid image
            if valid_image:
                
                # Image is good, we can break and continue with the conversion process
                break

        # Open the image with PIL
        object_image = Image.open(os.path.join(objects_folder, object_image_filename))

        # Get the size of the object image for XML generation
        original_object_image_width, original_object_image_height = object_image.size

        # Extract the raw filename from the image
        raw_object_filename, object_file_ext = os.path.splitext(object_image_filename)

        # Create a loop for checking positions until a valid position is found
        while True:

            # Choose a scale factor for the object
            scale_factor = random.uniform(1, 5)

            # Resize the object image to a reasonable size
            object_image = object_image.resize((round(original_object_image_width / scale_factor), round(original_object_image_height / scale_factor)))

            # Fix the size of the image
            object_image_width, object_image_height = object_image.size


            # Pick a random location for the position of the object in the frame
            object_position = [random.randint(round(-object_image_width / 2), round(image_width - (object_image_width / 2))), random.randint(round(-object_image_height / 2), round(image_height - (object_image_height / 2)))]

            # Create an object tuple (name, xmin, ymin, xmax, ymax)
            x_min = object_position[0]
            y_min = object_position[1]
            x_max = (object_position[0] + object_image_width)
            y_max = (object_position[1] + object_image_height)
            
            # Create an accumulator for checking validity
            invalid_object = False

            # Make sure the labels are valid
            # Overlap checking
            for object_info in image_objects:

                # Get the middle of the X and Y of the object
                object_x_middle = ((object_info[3] - object_info[1]) / 2) + object_info[1]
                object_y_middle = ((object_info[4] - object_info[2]) / 2) + object_info[3]

                # Check to make sure that the middle of the current object isn't going to interfere with the ranges of the other objects
                if x_min < object_x_middle and x_min > object_info[1]:
                    
                    # Left side of old object is covered, it's invalid
                    invalid_object = True

                elif x_max > object_x_middle and x_max < object_info[3]:

                    # Right side of old object is covered, it's invalid
                    invalid_object = True

                elif x_min < object_info[1] and x_max > object_info[3]:

                    # Whole object is engulfed
                    invalid_object = True

                elif y_min < object_y_middle and y_min > object_info[2]:
                    
                    # Top side of old object is covered, it's invalid
                    invalid_object = True

                elif y_max > object_y_middle and y_max < object_info[4]:
                    
                    # Bottom side of old object is covered, it's invalid
                    invalid_object = True

                elif y_min < object_info[2] and y_max > object_info[4]:

                    # Whole object is covered
                    invalid_object = True


            # Check to see if the left coordinate is off the screen, fix it if it is
            if x_min < 0:
                x_min = 0

            # Check to see if the top coordinate is off the screen, fix it if it is
            if y_min < 0:
                y_min = 0

            # Check to see if right coordinate is off the screen
            if x_max > image_width:
            
                # Off the right side, need to decide if this is a shrink or a removal
                if (object_image_width / 2) < (x_max - image_width):

                    # More than half of the object would be off the screen, this position is invalid
                    invalid_object = True

                else:
                    # Less than half of the object is off the screen, therefore we can just fix the label
                    x_max = image_width

            # Check to see if the lower coordinate is off the screen
            if y_max > image_height:

                # Off the bottom of the image, need to decide if this is a shrink or a removal
                if (object_image_height / 2) < (y_max - image_height):

                    # More than half of the object would be off the screen, this position is invalid
                    invalid_object = True

                else:
                    # Less than half of the object is off the screen, therefore we can just fix the label
                    y_max = image_height



            # If the object isn't invalid at this point, we can break and continue with the paste
            if not invalid_object:
                break

        # Fix the size of the image
        object_image_width, object_image_height = object_image.size

        # Create a default label for the object
        object_label = ""

        # Get the label for the object
        for object_name in image_objects_to_object_names:
            
            # The name matches, we can convert it to this
            if object_name[0] == object_image_filename:

                # Set the object label
                object_label = object_name[1]

                # Break from the loop, we're finished
                break


        # Convert the original image to a RGBA (with A being opacity, 0 = transparent)
        transparent_object = object_image.convert("RGBA")

        # Convert the image to a list of pixels
        transparent_object_data = transparent_object.getdata()

        # Create an accumulator for the pixels of the new image
        transparent_object_pixels = []

        # Loop through checking for white pixels, make them transparent if they're white
        for pixel in transparent_object_data:
            
            # Color must be white
            if pixel[0] >= 230 and pixel[1] >= 230 and pixel[2] >= 230:

                # Append a transparent white pixel to the list of pixels
                transparent_object_pixels.append((255, 255, 255, 0))
            else:

                # Just copy the pixel over
                transparent_object_pixels.append(pixel)

        # Changed the RGBA to the new transparent one
        transparent_object.putdata(transparent_object_pixels)

        # Paste that object's image into the current image (requires 2nd object image for mask)
        image.paste(object_image, object_position, transparent_object)

        # Create a list of object data
        object_data = [object_label, x_min, y_min, x_max, y_max]

        # Append an object to the object list
        image_objects.append(object_data)


    # Extract the raw filename from the image
    raw_image_filename, image_file_ext = os.path.splitext(input_image_filename)

    # Create a new filename for the image
    new_image_filename = raw_image_filename + ".jpg"

    # Save the image to the output directory
    image.save(os.path.join(output_path, "JPEGImages", new_image_filename))
    
    # Build the respective annotation file
    common_functions.build_xml_annotation(image_objects, new_image_filename, output_path)


main()