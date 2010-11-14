'''
Created on Nov 3, 2010

@author: surya
'''

import sys
import time
import json
import logging
import smtplib

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Collections.SuryaProcessingList import *
from Collections.SuryaProcessResult import *
from Logging.Logger import getLog
from Locking.AppLock import getLock
from GmailPortalSettings import setting
from mongoengine import *

connect('SuryaDB')


class GmailResults:
    
    log = getLog('GmailResults')
    
    def __init__(self):
        self.log.setLevel(logging.DEBUG)
    
    
    def run(self):
        '''
        '''
        
        self.log.info("[Running GmailResults]")
        
        COMMASPACE = ', '
        
        if not getLock('GmailResults', 'GmailResults'):
            return False
        
        self.running = True
        
        self.log.info("Checking email in every {0:s} seconds.".format(str(setting.get("poll_interval", 600))))            
        
        while self.running:
            try:
                self.running = self.checkResults()
            except Exception, err:
                self.log.critical("Unhandling Exception: " + str(sys.exc_info()[1]) + 'msg: ' + str(err))       
                break                    
            time.sleep(setting.get("poll_interval", 600))
            
        self.log.info("[Done Running GmailResults]")
            
    def checkResults(self):
        ''' 
        
        Returns:
        Boolean True if nothing is wrong; otherwise, False.
        '''
        
        gmail_user = setting.get("username")
        gmail_pwd = setting.get("password")
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(gmail_user, gmail_pwd)
        
        self.log.info("Start to checking Results... {0}".format(str(setting.get("poll_interval", 600))))
        
        for item in SuryaProcessingList.objects():
            
            try:
                misc = item.processEntity.misc
                misc_dict = json.loads(misc)
            except ValueError as ve:
                self.log.error('[ Sanity ] The misc input is not a json syntax string. Store it as { "rawstring": (...input...)} . The orignial Input:' + str(misc)+ "Reason:" + str(ve))
                misc = '{ "rawString":"' + str(misc) + '"}'
                
            if misc_dict.has_key("fromemail"):
                
                msg = MIMEMultipart('localhost')
                
                imgfile = item.processEntity.file
                text = ""
                
                for configuration in item.configurations:
                    for result in configuration.resultList:
                        
                        if not result.isEmailed:
                            # Fetch its preprocessing result
                            pprocResult = item.preProcessResultList[result.epoch-1]
                            
                            text = 'Results on PREPROCESSING the Image for Epoch: ' + str(result.epoch) + '\n'
                            text += 'Status: '+pprocResult.status+' UploadData InvalidReason(if any): '+item.processEntity.invalidReason + '\n\n'
                            
                            img = MIMEImage(pprocResult.debugImage.read())
                            img.add_header('content-disposition','attachment; filename="%s"'% pprocResult.debugImage.name)
                            msg.attach(img)
                            
                            text += 'Results on BLACK CARBON CONCENTRATION ANALYSIS on Image ' + imgfile.name + ' for Epoch: ' + str(result.epoch) + '\n'
                            if "Success" in result.status:    
                                text += 'filterRadius: ' + str(configuration.calibrationData.filterRadius) + '\n'
                                text += 'exposedTime: ' + str(configuration.calibrationData.exposedTime) + '\n'
                                text += 'bcStrip: ' + str(configuration.calibrationData.bcStrips) + '\n'
                                text += 'airFlowRate: ' + str(configuration.calibrationData.airFlowRate) + '\n'
                                text += 'BCAreaRed: ' + str(result.result.BCAreaRed) + '\n'
                                text += 'BCAreaGreen: ' + str(result.result.BCAreaGreen) + '\n'
                                text += 'BCAreaBlue: ' + str(result.result.BCAreaBlue) + '\n'
                                text += 'BCVolRed: ' + str(result.result.BCVolRed) + '\n'
                                text += 'BCVolGreen: ' + str(result.result.BCVolGreen) + '\n'
                                text += 'BCVolBlue: ' + str(result.result.BCVolBlue) + '\n\n'
                                
                                chartimg = MIMEImage(result.chartImage.read())
                                chartimg.add_header('content-disposition','attachment; filename="%s"'% result.chartImage.name)
                                msg.attach(chartimg)
                                
                            else:
                                text += 'Status: '+result.status+' UploadData InvalidReason(if any): '+item.processEntity.invalidReason
                            
                            result.isEmailed = True
                            pprocResult.isEmailed = True
                            
                    for pprocItem in item.preProcessResultList:
                        if not pprocItem.isEmailed:
                            text += 'Results on PreProcessing the Image for Epoch' + str(result.epoch) + '\n'
                            text += 'Status: '+pprocResult.status+' UploadData InvalidReason(if any): '+item.processEntity.invalidReason + '\n'
                            
                            img = MIMEImage(pprocResult.debugImage.read())
                            img.add_header('content-disposition','attachment; filename="%s"'% pprocResult.debugImage.name)
                            msg.attach(img)
                            pprocResult.isEmailed = True
                
                
                if text is not "":
                    msg['From'] = setting.get("username")
                    msg['To'] = misc_dict["fromemail"]
                    msg['Subject'] = 'Result Mail for ' + imgfile.name
                    # Attach the text
                    msgtext = MIMEText(text, 'plain')
                    msg.attach(msgtext)
                    
                    # Attach the images
                    img = MIMEImage(imgfile.read())
                    img.add_header('content-disposition','attachment; filename="%s"'% imgfile.name)
                    msg.attach(img)
                    
                    # TODO: remove my email id
                    smtpserver.sendmail(setting.get("username"), misc_dict["fromemail"], msg.as_string())
                    self.log.info("sent email")
                    item.save()
                                        
        smtpserver.close()

        return True
    
if __name__ == '__main__':
    g = GmailResults()
    g.run()   