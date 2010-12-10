'''
Created on Dec 5, 2010

@author: surya
'''

import sys
import json
import logging
from mongoengine import *

from datetime import datetime
from Logging.Logger import getLog
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Context, loader, RequestContext


from Collections.SuryaUploadData import *
from Collections.SuryaDeploymentData import *
from Collections.SuryaCalibrationData import *
from SuryaWebPortal.exceptions.UploadException import UploadException 
from Collections.SuryaProcessingList import *
import mongoengine

# Connect to MongoDB
connect('SuryaDB')

log = getLog('views')
log.setLevel(logging.DEBUG)



def home(request):
    t = loader.get_template('layout.html')
    c = RequestContext(request, {'yes': True})
    return HttpResponse(t.render(c))
