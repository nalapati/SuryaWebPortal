'''
Created on Nov 1, 2010

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


# The cell phone expect the following line as an OK signal in the first line
CUSTOMIZED_PHONE_STATUS_OK   = "upok "
CUSTOMIZED_PHONE_STATUS_FAIL = "svrfail "

@csrf_exempt
def upload_image(request):
    ''' This view gets invoked when uploading data to the server. The 
        post params are validated and stored in the SuryaUploadData
        Collection and the data files uploaded are stored in GridFS
    '''
    
    if (request.method == 'POST'):
        try:
            # Check if post has the device_id
            if 'device_id' not in request.POST:
                raise UploadException('[ Sanity ] Missing mandatory field [device_id] in POST fields.')
            else:
                device_id = request.POST["device_id"]
                valid_flag = True
                invalid_reason = ""
                
            server_datetime = datetime.now()
            
            # Check if post has the aux_id field
            if 'aux_id' in request.POST:
                aux_id = request.POST["aux_id"]
            else:
                log.info('[ Sanity ] Missing [aux_id] in POST fields.')
                aux_id = ""
                
            # TODO : extract calibration data from the misc field
            if 'misc' in request.POST:
                try:
                    misc = request.POST["misc"]
                    misc_dict = json.loads(misc)
                except ValueError as ve:
                    log.error('[ Sanity ] The misc input is not a json syntax string. Store it as { "rawstring": (...input...)} . The orignial Input:' + str(misc)+ "Reason:" + str(ve))
                    misc = '{ "rawString":"' + str(misc) + '"}'
            else:
                log.info('Missing [misc] in POST fields.')
                misc = ""

            #validation on client datetime
            if 'record_datetime' in request.POST:
                try:
                    record_datetime = eval ("datetime(" + request.POST["record_datetime"] + ")")
                except:
                    valid_flag = False
                    invalid_reason += "The record_datetime provided by the client is not in a valid format.<br/>"
                    record_datetime = datetime(1999,1,1,1,1,1)
                    log.warning('The record_datetime provided by the client is not in a valid format. For example, a right example is "2010,6,19,16,18,00" (Year, Month, Day, Hour, Minute, Second). <br/> Details: <br/>' + str(sys.exc_info()))                     
            else: #record_datetime is missing
                valid_flag = False
                invalid_reason += "Missing [record_datetime] in POST fields.<br/>"
                log.warning("Missing [record_datetime] in POST fields.")
                record_datetime = datetime(1999,1,1,1,1,1)
                
            # GPS data
            (gps_longitude, gps_latitude, gps_altitude) = (0.0, 0.0, 0.0) # a default value
            if 'gps' in request.POST:
                gps = request.POST["gps"]
                try:
                    gps_values = [ val.strip() for val in gps.split(",") ]
                    if len(gps_values)==3:
                        (gps_longitude, gps_latitude, gps_altitude) = [float(val) for val in gps_values] #overwrite with correct value
                    else:
                        log.warning("The format of GPS seems to be corrupted. It must contains three float numbers and be seperated by comma.")
                except:
                    log.warning("The format of GPS seems to be corrupted. <br/> Details <br/>" + str(sys.exc_info()))
            else:
                log.info("Missing [gps] in POST fields.")
                
            if 'data_type' in request.POST:       
                data_type = request.POST["data_type"]
            else:
                log.info("Missing [data_type] in POST fields.")
                data_type = ""

            if 'tag' in request.POST:
                tag = request.POST["tag"]
            else:
                log.info("Missing [tag] in POST fields.")
                tag = ""

            if 'version' in request.POST:
                version = request.POST["version"]
            else:
                log.info("Missing [version] in POST fields.")
                version = ""

            if 'deployment_id' in request.POST:
                deployment_id = request.POST["deployment_id"]
            else:
                log.info("Missing [deployment_id] in POST fields.")
                 
            strMeta = "device_id:%(device_id)s, server_datetime:%(server_datetime)s, aux_id:%(aux_id)s, misc:%(misc)s, record_datetime:%(record_datetime)s, gps: %(gps_longitude)s %(gps_latitude)s %(gps_altitude)s, data_type:%(data_type)s, tag:%(tag)s, version:%(version)s, deployment_id:%(deployment_id)s, valid_flag:%(valid_flag)s, invalid_reason:%(invalid_reason)s" % \
            {"device_id": device_id, "server_datetime": server_datetime, "aux_id": aux_id, "misc": misc, "record_datetime": record_datetime, "gps_longitude": gps_longitude, "gps_latitude": gps_latitude, "gps_altitude": gps_altitude, "data_type": data_type, "tag": tag, "version": version, "deployment_id": deployment_id, "valid_flag":valid_flag, "invalid_reason":invalid_reason}

            ##########################
            # Prepare for saving image

            #Get Server Time String
            datetime_str = server_datetime.strftime("%Y%m%d.%H%M%S.") # e.g '20100702.174502.' 
            img_filename = datetime_str + device_id + ".jpg"
                       
            if 'bin_file' not in request.FILES:
                raise UploadException("[ Sanity ] Missing mandatory field [bin_file] in POST fields.")       

                    ######################################
            # Prepare saving meta info to database 
            try:
                #Save metadata to DB   
                dbRecord = SuryaUploadData(
                deviceId=device_id, \
                serverDatetime=server_datetime, 
                filename=img_filename,
                auxId=aux_id, \
                misc=misc, 
                recordDatetime=record_datetime, \
                gpsLongitude=gps_longitude, 
                gpsLatitude=gps_latitude, 
                gpsAltitude=gps_altitude, \
                datatype=data_type, 
                tag=tag, 
                version=version, \
                validFlag=valid_flag, 
                invalidReason=invalid_reason, \
                deploymentId=deployment_id)
                
                try:
                    # Save uploaded image
                    dbRecord.file.new_file(filename = img_filename, content_type = 'image/jpeg')
                    for chunk in request.FILES['bin_file'].chunks():
                        dbRecord.file.write(chunk)
                    dbRecord.file.close()
                except:
                    raise UploadException("[ SavingFile ] Errors while attempting to save the uploading file. <br/> Details: <br/>" + str(sys.exc_info()[1]))
                
                dbRecord.save()
                
                # This method varies from application to application gotta make it generic
                #Save this dbRecord reference in the ProcessList, get default processing data
                # TODO invoke this as a method
                for item in SuryaDeploymentData.objects(deploymentId=deployment_id):
                    # currently no datetime check, no validation as in if any one of the following is missing 
                    # this item doesn't get added to the process list
                    
                    if isinstance(item.calibrationId, SuryaImageAnalysisBCStripData):
                        log.info('got bcstrip data')
                        bcStripData = item.calibrationId
                    elif isinstance(item.calibrationId, SuryaImageAnalysisCalibrationData):
                        log.info('got img analysis calib data')
                        calibData = item.calibrationId
                    elif isinstance(item.calibrationId, SuryaImagePreProcessingCalibrationData):
                        log.info('got img pre proc calib data')
                        pprocData = item.calibrationId
                
                SuryaIANAProcessingList(processEntity=dbRecord,
                                        processingFlag=False,
                                        processedFlag=False,
                                        overrideFlag=True, 
                                        preProcessingConfiguration=pprocData, 
                                        computationConfiguration=calibData, 
                                        bcStrips=bcStripData).save()
                 
            except:
                raise UploadException("[ AccessDatabase ] Errors while attempting to save meta info to the suryaDB database."+
                                          " <br/> Details: <br/>" + str(sys.exc_info()[1]))

        except UploadException as ue:
            log.error(ue.str)
            strRet = CUSTOMIZED_PHONE_STATUS_FAIL + ":" + ue.str
        except:
            log.critical("[ Developer ] Unhandling Exception: " + str(sys.exc_info()[1]))
            strRet = CUSTOMIZED_PHONE_STATUS_FAIL + ":" + str(sys.exc_info()[1])
        else:
            #################################
            # Prepare for returning & logging

            strRet = CUSTOMIZED_PHONE_STATUS_OK
            strRet += "Your uploading file has been stored at " + img_filename + ". \n"
            strRet += strMeta
            log.info("[ test_tag ] " + strRet)
        

        return HttpResponse(content=strRet, mimetype=None, status=200, content_type='text/html')
    
    else:
        log.error('[ Protocol ] Received a non POST request')
        return HttpResponse('Server accepts only HTTP POST messages')
