'''
Created on Nov 1, 2010

@author: surya
'''

class UploadException(Exception):
    
    def __init__(self, str):
        ''' Constructs the Upload Exception, which is raised
            whenever an error occurs while a client uploads
            data to the server.
            
        Keyword Arguments:
        str -- String, message representing the cause for the exception
        '''
        self.str = str