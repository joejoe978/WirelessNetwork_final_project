import os
import glob

def getFileInDirectory(path):

    #path = "/Volumes/Transcend/GitHub/WNFA_FinalProject/new_src/AoA"
    file_list = []
    for filename in glob.glob(os.path.join(path, '*.png')):
        file_list.append(filename)
    return sorted(file_list)