
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



def uploadfile(request, objID=None):
    if objID is None:
        return HttpResponseNotFound('<h1>File not found</h1>')

    try:
        upload = SuryaUploadData.objects.with_id(objID)
    except ValidationError:
        return HttpResponseNotFound('<h1>File Upload not found</h1>')
    
    try:
        data = upload.origFile.read()
        content_type = upload.origFile.content_type
    except AttributeError:
        return HttpResponseNotFound('<h1>File DB not found</h1>')
    
    return HttpResponse(data, mimetype=content_type)


def chartfile(request, objID=None):
    if objID is None:
        return HttpResponseNotFound('<h1>File not found</h1>')

    try:
        result = SuryaIANAResult.objects.with_id(objID)
    except ValidationError:
        return HttpResponseNotFound('<h1>File not found</h1>')

    try:
        data = result.computationResult.chartImage.read()
        content_type = result.computationResult.chartImage.content_type
    except AttributeError:
        return HttpResponseNotFound('<h1>File not found</h1>')
    
    return HttpResponse(data, mimetype=content_type)


def debugfile(request, objID=None):
    if objID is None:
        return HttpResponseNotFound('<h1>File not found</h1>')

    try:
        result = SuryaIANAResult.objects.with_id(objID)
    except ValidationError:
        return HttpResponseNotFound('<h1>File not found</h1>')

    try:
        data = result.preProcessingResult.debugImage.read()
        content_type = result.preProcessingResult.debugImage.content_type
    except AttributeError:
        return HttpResponseNotFound('<h1>File not found</h1>')
    
    return HttpResponse(data, mimetype=content_type)


    
