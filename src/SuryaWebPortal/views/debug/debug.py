
import sys
import json
import logging
from mongoengine import *

from datetime import datetime
from Logging.Logger import getLog
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from Collections.SuryaUploadData import *
from Collections.SuryaGroundTruth import *
from Collections.SuryaDeploymentData import *
from Collections.SuryaProcessingList import *
from Collections.SuryaProcessResult import *
from Collections.SuryaCalibrationData import *


import mongoengine

# Connect to MongoDB
connect('SuryaDB')

log = getLog('views')
log.setLevel(logging.DEBUG)


@login_required
def debug(request):
    if not request.user.is_staff:
        return redirect('SuryaWebPortal.views.home.home')
    
    t = loader.get_template('debug/debug.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

@login_required
def uploads(request, objID=None):
    if not request.user.is_staff:
        return redirect('SuryaWebPortal.views.home.home')
    
    t = loader.get_template('debug/uploads.html')
    if objID is None:
        c = RequestContext(request, {'uploads' : SuryaUploadData.objects})
    else:
        c = RequestContext(request, {'uploads' : [SuryaUploadData.objects.with_id(objID)]})
    
    return HttpResponse(t.render(c))

@login_required
def results(request):
    if not request.user.is_staff:
        return redirect('SuryaWebPortal.views.home.home')
    t = loader.get_template('debug/results.html')
    c = RequestContext(request, {'results' : SuryaIANAResult.objects})
    return HttpResponse(t.render(c))


@login_required
def failures(request):
    if not request.user.is_staff:
        return redirect('SuryaWebPortal.views.home.home')
    if not request.user.is_staff:
        return redirect('SuryaWebPortal.views.home.home')
    t = loader.get_template('debug/failures.html')
    c = RequestContext(request, {'failures' : SuryaIANAFailedResult.objects})
    return HttpResponse(t.render(c))


