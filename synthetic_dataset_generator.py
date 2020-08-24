# Written by Christian Piper
# First Robotics Team 834
# Created: 8/23/20

# Import libraries
import common_functions
from PIL import Image
import random
import shutil
import os

# Resources folder for available objects
objects_folder = "./resources/object_images"
image_objects_to_object_names = [["ball.jpg", "Power_Cell"], ["ball2.jpg", "Power_Cell"], ["ball3.jpg", "Power_Cell"]]

def main():
    deletion_files = common_functions.get_all_file_paths("/home/cap1sup/Desktop/Robotics/MLFlex/testing/Annotations") + common_functions.get_all_file_paths("/home/cap1sup/Desktop/Robotics/MLFlex/testing/JPEGImages")
    for file_ in deletion_files:
        os.remove(file_)
    create_synthetic_image("test.jpg", "/home/cap1sup/Desktop/Robotics/MLFlex/testing/", "/home/cap1sup/Desktop/Robotics/MLFlex/testing", 3)


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
        old_object_image_width, old_object_image_height = object_image.size

        # Choose a scale factor for the object
        scale_factor = random.uniform(1, 5)

        # Resize the object image to a reasonable size
        object_image = object_image.resize((round(old_object_image_width / scale_factor), round(old_object_image_height / scale_factor)))

        # Fix the size of the image
        object_image_width, object_image_height = object_image.size

        # Extract the raw filename from the image
        raw_object_filename, object_file_ext = os.path.splitext(object_image_filename)

        # Create a loop for checking positions until a valid position is found
        while True:

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
    new_image_filename = raw_image_filename + "_modified.jpg"

    # Save the image to the output directory
    image.save(os.path.join(output_path, "JPEGImages", new_image_filename))
    
    # Build the respective annotation file
    common_functions.build_xml_annotation(image_objects, new_image_filename, output_path)


main()