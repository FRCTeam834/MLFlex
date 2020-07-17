import shutil
import os

paths_to_delete = ["testing\RasPi", "testing\Rio"]

for path in paths_to_delete:
    path = os.path.abspath(path)
    if os.path.isdir(path):
        shutil.rmtree(path)
