
import sys
import json
import logging
from mongoengine import *

from datetime import datetime
from Logging.Logger import getLog
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader, RequestContext


from Collections.SuryaUploadData import *
from Collections.SuryaProcessResult import *
import mongoengine

# Connect to MongoDB
connect('SuryaDB')

log = getLog('views')
log.setLevel(logging.DEBUG)


def oneoffresult(request, objID=None):
    if objID is None:
        return HttpResponseNotFound('<h1>File not found</h1>')

    try:
        result = SuryaIANAResult.objects.with_id(objID)
    except ValidationError:
        return HttpResponseNotFound('<h1>File not found</h1>')
    
    t = loader.get_template('result.html')
    c = RequestContext(request, {'result' : result})
    
    return HttpResponse(t.render(c))

