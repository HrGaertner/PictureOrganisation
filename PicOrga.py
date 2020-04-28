# !/usr/bin/python
from optparse import OptionParser
import os
import shutil
import json
import sqlite3


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

# Datenbank um Duplikate zu indentifizieren.
if os.path.isfile(d_dir + "pics.db"):
    database = sqlite3.connect(d_dir + "pics.db")
    database_cursor = database.cursor()
else:
    database = sqlite3.connect(d_dir + "pics.db")
    database_cursor = database.cursor()
    database_cursor.execute("CREATE TABLE pics_sum (sum TEXT)")
    database.commit()

pic_types = (".png", ".jpeg", ".jpg", ".gif", ".webp", ".tiff", ".psd", ".raw", ".bmp", ".heif", ".indd", ".jp2",
             ".svg", ".ai", ".eps", ".pdf", ".jpe", ".jif", ".jfif", ".jfi", ".tif", ".arw", ".cr2", ".k25", ".dib",
             ".ind", ".indt", ".j2k", ".jpf", ".jpx", ".jpm", ".mj2", ".svgz")


# Recursive Function which search a dir for pics processes them and returns the sub dirs.
def search_dir(path):
    if options.pics_only:
        # Checking for pics and dirs
        dir_content = [item for item in os.listdir(path) if not os.path.isfile(path + item) or item.endswith(pic_types)]
    else:
        dir_content = os.listdir(path)
    for content in dir_content:
        if os.path.isfile(path + content):
            # Getting the Meta Information needed to get the age of the file
            infos = json.loads(os.popen("mediainfo '" + path + content + "' -f --Output=JSON").read())
            date = infos["media"]["track"][0]["File_Modified_Date_Local"]
            year = date[:4] + "/"
            month = date[5:7] + "/"
            file_name = date[8:10] + "-" + date[-8:] + "." + content.split(".")[-1]
            md5sum = os.popen("md5sum " + path + content).read().split("  ")[0]
            database_cursor.execute("SELECT sum FROM pics_sum where sum='" + md5sum + "'")
            if not database_cursor.fetchall():
                database_cursor.execute("INSERT INTO pics_sum VALUES ( '" + md5sum + "' ) ")
                database.commit()
                try:
                    os.mkdir(d_dir + year)
                except FileExistsError:
                    pass
                try:
                    os.mkdir(d_dir + year + month)
                except FileExistsError:
                    pass
                if os.path.isfile(s_dir + year + month + file_name):
                    i = 0
                    while os.path.isfile(s_dir + year + month + file_name + i):
                        i += 1
                    shutil.copyfile(path + content, d_dir + year + month + file_name + i)
                shutil.copyfile(path + content, d_dir + year + month + file_name)
            if options.remove:
                os.remove(path + content)
        else:
            search_dir(path + content + "/")
            if options.remove:
                shutil.rmtree(path + content)


search_dir(s_dir)

database.commit()
database.close()
