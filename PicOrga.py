# !/usr/bin/python
from optparse import OptionParser
import os
import shutil
import subprocess


# Parsing the arguments for the directory of unsorted pictures and the directory of the sorted.
parser = OptionParser()
parser.add_option("-s", "--source-directory", dest="s_dir",
                  help="Root directory of your photo collection (please with / in the end)", metavar="SourceDir")
parser.add_option("-d", "--destination-directory", dest="d_dir",
                  help="Directory where your new sorted photo collection will be created (also with / in the end)")
parser.add_option("-r", "--remove-after-process", dest="remove", action="store_true",
                  help="After copying and processing file the pic will be deleted in the source directory",
                  default=False)
parser.add_option("-p", "--only-pictures", dest="pics_only", action="store_true",
                  help="If you have other files in the dir which should not be taken with to the new structure (because\
                   they are no picture)", default=False)

(options, args) = parser.parse_args()
s_dir = options.s_dir
d_dir = options.d_dir

pic_types = (".png", ".jpeg", ".jpg", ".gif", ".webp", ".tiff", ".psd", ".raw", ".bmp", ".heif", ".indd", "jp2",
             ".svg", ".ai", ".eps", ".pdf", ".jpe", ".jif", ".jfif", ".jfi", ".tif", ".arw", "cr2", "k25", ".dib",
             "ind", "indt", "j2k", "jpf", "jpx", "jpm", "mj2", "svgz")


# Recursive Function which search a dir for pics processes them and returns the sub dirs.
def search_dir(path):
    if options.pics_only:
        # Checking for pics and directorys
        dir_content = [item for item in os.listdir(path) if not os.path.isfile(path + item) or item.endswith(pic_types)]
    else:
        dir_content = os.listdir(path)
    for content in dir_content:
        if os.path.isfile(path + content):
            print(content)
            if options.remove:
                os.remove(path + content)
        else:
            search_dir(path + content + "/")
            if options.remove:
                shutil.rmtree(path + content)


search_dir(s_dir)
