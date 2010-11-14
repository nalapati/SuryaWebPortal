'''
Created on Nov 1, 2010

@author: surya
'''

import os
import sys
import json
import time

from datetime import datetime
from Collections.SuryaUploadData import *
from Collections.SuryaGroundTruth import *
from Collections.SuryaDeploymentData import *
from Collections.SuryaProcessingList import *
from Collections.SuryaCalibrationData import *
from django.core.management.base import BaseCommand, CommandError
#from DataAnalyzer.DataAnalyzer import cronjob
from SuryaWebPortal.gmailportal.GmailPortal import GmailPortal

class Command(BaseCommand):
    args = 'calibrationfile'
    help = 'Initializes the Server: \n 1. Checks if mongod is running \n 2. Checks if mongoengine is installed'
     
    def handle(self, *args, **options):
        ''' The SuryaWebPortal initialization method.
        '''
        
        # Check if we have the right number of arguments
        if len(args) != 1:
            raise CommandError('Error insufficient params: use ./manage.py init -help for info')
        
        # Check if mongod, is running
        isMongod = False
        processes = os.popen('''ps axo "%c"''')
        for process in processes:
            if 'mongod' in process:
                isMongod = True
        
        if not isMongod:
            raise CommandError('Error please run mongod first')
        
        # Import mongoengine and connect to the database
        try:
            import mongoengine
        except:
            raise CommandError('Error importing from mongoengine. Please ensure that mongoengine is installed')
        
        # Drop the database SuryaDB (This Implies That we lose all the stored images as well)
        mongoengine.connect('SuryaDB')
        SuryaUploadData.drop_collection()
        SuryaGroundTruth.drop_collection()
        SuryaDeploymentData.drop_collection()
        SuryaCalibrationData.drop_collection()
        SuryaProcessingList.drop_collection()
        
        # Initialize the DB with default Calibration data.            
        calibrationDataList = json.loads(open(args[0],'r').read())
        
        for calibrationDataEntry in calibrationDataList:
            calibrationData = SuryaImageAnalysisCalibrationData(calibrationId = calibrationDataEntry.get("calibrationId"),
                                                                exposedTime   = calibrationDataEntry.get("exposedTime"),
                                                                airFlowRate   = calibrationDataEntry.get("airFlowRate"),
                                                                filterRadius  = calibrationDataEntry.get("filterRadius"),
                                                                bcArea        = calibrationDataEntry.get("bcArea"),
                                                                bcStrips      = calibrationDataEntry.get("bcStrips"))
            calibrationData.save()
            deploymentDataList = calibrationDataEntry.get("deploymentIds")
            # Initialize the DB with default DeploymentId to CalibrationData mapping
            for deploymentDataEntry in deploymentDataList:
                SuryaDeploymentData(deploymentId=deploymentDataEntry.get("deploymentId"),
                                    activateDatetime=datetime(*deploymentDataEntry.get("activateDatetime")),
                                    calibrationId=calibrationData).save()

        # Run the Django Webserver
        os.popen('''/home/surya/Production/SuryaWebPortal/src/SuryaWebPortal/manage.py runserver &''')
        
        # Initialize the Image Analysis Controller.
        os.popen('''python /home/surya/Production/SuryaIANAFramework/src/IANA/IANAFramework.py &''')
        
        # Start the gmail monitor.
        os.popen('''python /home/surya/Production/SuryaWebPortal/src/SuryaWebPortal/gmailportal/GmailPortal.py &''')
        
        # Result Mailer.
        os.popen('''python /home/surya/Production/SuryaWebPortal/src/SuryaWebPortal/gmailportal/GmailResults.py &''')
