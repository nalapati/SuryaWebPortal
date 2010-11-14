'''
Created on Nov 2, 2010

@author: surya
'''

'''
Created on Oct 30, 2010

@author: surya
'''

import os
import sys
import logging

from Logging.Logger import getLog

log = getLog('FileCache')
log.setLevel(logging.INFO)

# TODO: something about this i.e. port to settings
root = os.path.dirname(__file__) + '/imagecache/'

def put(filename, filedata):
    ''' Saves the filedata in a file represented by filename in the filecache
    
    Keyword Arguments:
    filename  -- The name of the file
    filedata  -- The data to store in the file

    Returns:
    String -- The Absolute file path if file was saved successfully, None otherwise
    '''
    
    try:
        absfilename = root + filename
        fh = open(absfilename, "wb") #DEBUG
        fh.write(filedata)
        fh.close()
        os.chmod(absfilename, 0777)  #In Debug Mode, set the image file permission to 777
            
        log.info("Successfully saved the file '" + absfilename + "'") 
        return absfilename
    except:
        log.error("Failed to save the file '" + absfilename + "'" + ":" + str(sys.exc_info()[1])) 
        return None
        
# TODO: maintain a list of files that we failed to delete and get a reaper to delete them later
def remove(filename):
    ''' Removes the file represented by filename from the filecache
    
    Keyword Arguments:
    filename -- The name of the file
    '''
    
    os.remove(root+filename)