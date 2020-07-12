# Import libraries
from annotations import convert_Supervisely_2_Pascal_VOC, get_image_objects
import argparse 
import shutil
import os

def main():

    # Initialize parser 
    parser = argparse.ArgumentParser(description = 'MLFlex: A quick and easy annotation manipulation tool') 

    # Create required argument group
    required_args = parser.add_argument_group('required arguments')

    # Add arguments
    # String arguments
    required_args.add_argument("-i", "--input",  required = True, help = "Input path to the folder containing the Supervisely annotations.")
    required_args.add_argument("-o", "--output", required = True, help = "Output path for the .zip file")

    # Boolean arguments
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


main()