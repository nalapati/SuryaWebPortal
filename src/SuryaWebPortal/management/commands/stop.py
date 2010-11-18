'''
Created on Nov 5, 2010

@author: surya
'''

import os

from django.core.management.base import BaseCommand, CommandError

processlist = ['SuryaWebPortal/manage.py runserver',
               'IANAFramework.py',
               'IANAGmailResults.py',
               'IANAGmailMonitor.py']

class Command(BaseCommand):
    args="all"
    help="the 'all' option closes all SuryaWebPortal related processes"
    
    def handle(self, *args, **options):
        ''' The SuryaWebPortal Quit method
        '''

        if len(args) < 1:
            raise CommandError('Error insufficient params: use ./manage.py stop -help for info')
        
        if args[0] == 'all':
            processEntries = os.popen('''ps --width 1000 -eo "%p#%a" | grep "python"''')
            for processEntry in processEntries:
                if 'ps --width' not in processEntry:
                    pid, command = processEntry.split('#')
                    for process in processlist:
                        if process in command:
                            os.popen('''kill -9 '''+pid)
        

        