# Written by Christian Piper and William Corvino
# First Robotics Team 834
# Created: 8/23/20

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


def build_xml_annotation(objects, image_name, output_folder):

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
