#!/usr/bin/python
import exif
import sys
from datetime import datetime

def get_original_datetime_N80(filename):
    ''' Extracted the date time when the picture is taken.

    Keyword arguments:
    filename -- The full file name toward the image file to be processed.

    Returns:
    status   -- True if everything is fine; othewise, False
    detail   -- Datetime information from exif tag if status is true;
                otherwise, the detail of exception.
    '''
    try:
        with open(filename, 'r') as f:
            exif_data = exif.process_file(f, stop_tag='DateTimeOriginal') #stop after finding this tag
            str_original_datetime = exif_data.get("EXIF DateTimeOriginal").values # N80 okay
    except:
        return (False, str(sys.exc_info()))


    # Example in N80, 2010:08:24 17:02:58
    return (True, datetime.strptime(str_original_datetime, "%Y:%m:%d %H:%M:%S"))


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print("usage: " + sys.argv[0] + " <image filename>")
    else:
        (status, detail) = get_original_datetime_N80(sys.argv[1])
        print("Processing Results: " + str(status))
        print("Detail            : " + str(detail))
