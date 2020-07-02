import os

output_directory = './output/'

for filename in os.listdir(output_directory):
    os.remove(output_directory + filename)