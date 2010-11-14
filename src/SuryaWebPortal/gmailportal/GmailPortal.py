'''
Created on Oct 30, 2010

@author: surya
'''

import os
import sys
import time
import json
import email
import rfc822
import pycurl
import imaplib
import logging
import cStringIO

from ImageCache import put
from sampleExifN80 import get_original_datetime_N80
from Logging.Logger import getLog
from Locking.AppLock import getLock
from GmailPortalSettings import setting

# TODO: configuring logging so that critical messages get printed and logged

class GmailPortal:
    
    log = getLog('GmailPortal')
    
    def __init__(self):
        self.log.setLevel(logging.DEBUG)
    
    
    def run(self):
        '''
        '''
        
        self.log.info("[Running GmailPortal]")
        
        if not getLock('GmailPortal', 'GmailPortal'):
            return False
        
        self.running = True
        
        self.log.info("Checking email in every {0:s} seconds.".format(str(setting.get("poll_interval", 600))))            
        
        while self.running:
            try:
                self.running = self.checkInbox()
            except:
                self.log.critical("Unhandling Exception: " + str(sys.exc_info()[1]))       
                break                    
            time.sleep(setting.get("poll_interval", 600))
            
        self.log.info("[Done Running GmailPortal]")
            
    def checkInbox(self):
        ''' 
        
        Returns:
        Boolean True if nothing is wrong; otherwise, False.
        '''
        
        #Login: ('OK', ['20'])
        self.log.info("Start to checking Gmail... {0}".format(str(setting.get("poll_interval", 600))))            
        gmailConn = imaplib.IMAP4_SSL(setting.get("imap_host"), setting.get("imap_port"))
        
        (status, rsps) = gmailConn.login(setting.get("username"), setting.get("password"))
        if status == 'OK':
            self.log.info("Login successfully username: " + setting.get("username"))
        else:
            self.log.error("Login fail." + str(status) + ":" + str( rsps))
            return False
        
        #Select INBOX: ('OK', ['20'])
        (status, rsps) = gmailConn.select("INBOX")
        if status == 'OK':
            self.log.info("Selecting INBOX successfully.")
        else:
            self.log.error("Cannot select INBOX" + str(status) + ":" + str( rsps))
            return False
        
        # Search UNSEEN UNDELETED: ('OK', ['1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19'])
        (status, rsps) = gmailConn.search(None, "(UNSEEN UNDELETED)")
        mailIds = rsps[0].split()
        if status == 'OK':
            self.log.info("Finding {0:s} new emails.".format(str(len(mailIds))) +
                 ("unprocessed mail ids: " + rsps[0]) if len(mailIds) else "")
        else:
            self.log.error("Errors while searching (UNSEEN UNDELETED) mails."+ str(status) + ":" + str(rsps))
            return False
        
        for mid in mailIds:
            (status, rsps) = gmailConn.fetch(mid, '(RFC822)')
            if status == 'OK':
                self.log.info("Successfully fetching mail (mail id:{0:s})...".format(str(mid)))                    
            else:
                self.log.error("Errors while fetching mail (mail id:{0:s})...".format(str(mid)))
                continue
            
            mailText = rsps[0][1]
            mail = email.message_from_string(mailText)
            
            fromField = rfc822.parseaddr(mail.get("FROM"))[1]
            toField = rfc822.parseaddr(mail.get("TO"))[1]
            
            subjectField = mail.get("SUBJECT") # should be szu###
            if "szu" not in subjectField:
                self.log.error("Errors while fetching mail (mail id:{0:s})... It does not have szu in subjectField".format(str(mid)))
                continue
            if "Result" in subjectField:
                continue
            
            #TODO: add spam detection: only from "surya." with subject "szu" is considered valid.
            self.log.info("The mail (id: {0:s}) is from: <{1:s}> with subject: {2:s}" 
                          .format(str(mid), fromField, subjectField))
            
            message = mail.get_payload(decode=True)
            if message is not None:
                configDict = dict([v.split(':', 1) for v in message.splitlines() if ':' in v])
                configDict["fromemail"] = fromField
                for key in configDict.keys():
                    #TODO: move these keys to settings module 
                    if key not in setting.get("config_keys"):
                        del configDict[key]
            else:
                configDict = {"fromemail":fromField}
            
            message = json.dumps(configDict)
                                    
            
            #Downloading attachment from gmail
            parts = mail.walk()
            for p in parts:
                if p.get_content_maintype() !='multipart' and p.get('Content-Disposition') is not None:
                     
                    fdata = p.get_payload(decode=True)
                    filename = p.get_filename()
                    # Store the file in the file cache
                    picFileName = put(p.get_filename(), fdata)
                    
                    if picFileName is None:
                        self.log.error('Could Not save ' + filename + ' in the cache')
                        continue
                    else:
                        #Reading EXIF info
                        (status, pic_datetime_info) = get_original_datetime_N80(picFileName)
                        
                    if status:
                        self.log.info("From Exif metadata, the picture {0:s} is taken at {1:s}"
                             .format(picFileName, pic_datetime_info.strftime("%Y,%m,%d,%H,%M,%S")).replace(',0',','))
                    else:
                        self.log.error("Cannot get original datetime from picture: " + picFileName + "details: " + str(pic_datetime_info))
                        continue # try next part
                    
                    #Uploading to http server
                    
                    response = cStringIO.StringIO()

                    curl = pycurl.Curl()
                    curl.setopt(curl.WRITEFUNCTION, response.write)
                    curl.setopt(curl.POST, 1)
                    curl.setopt(curl.URL, setting.get("upload_url"))
                    curl.setopt(curl.HTTPPOST,[
                        ("device_id", subjectField),
                        ("aux_id", ""), #TODO: using CronJob to read QR code
                        ("misc", message), #not used
                        ("record_datetime", pic_datetime_info.strftime("%Y,%m,%d,%H,%M,%S").replace(',0',',')), #change 08->8, otherwise the server will complaints because we cannot run datetime(2010,08,23,18,1,1)
                        #("gps", ""), #not used
                        ("data_type", "image/jpeg"),
                        ("version", setting.get("http_post_version")),
                        ("deployment_id", toField[0:toField.index('@')]), #e.g. surya.pltk1 ("from email")
                        ("tag", ""), #not used  
                        ("bin_file", (curl.FORM_FILE, picFileName))
                        ])
                    curl.perform()
                    self.log.info("Running http post to: "+setting.get("upload_url"))
                    server_rsp = str(response.getvalue())
                    curl.close()
                    if str(server_rsp).startswith("upok"):
                        self.log.info("Successfully Uploading."+ str(server_rsp))
                    else:
                        self.log.error("The server returns errors."+ str(server_rsp))
                    os.remove(picFileName)        
                    self.log.info("Deleting uploaded temporary file: " + str(picFileName))  
                    
        gmailConn.close()
        gmailConn.logout()

        return True
    
if __name__ == '__main__':
    g = GmailPortal()
    g.run()    