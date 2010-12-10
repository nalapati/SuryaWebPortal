import os
import sys
import socket

os.environ['DJANGO_SETTINGS_MODULE'] = 'SuryaWebPortal.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

os.environ['SURYA_DEPLOY_ROOT'] = '/home/surya/deployed'

mypath = [os.getenv('SURYA_DEPLOY_ROOT') + '/SuryaWebPortal/src/']

for p in mypath:
	if p not in sys.path:
		sys.path.append(p)

#def application(environ, start_response):
#    status = '200 OK'
#    if not environ['mod_wsgi.process_group']:
#      output = 'EMBEDDED MODE'
#    else:
#      output = 'DAEMON MODE'
#    response_headers = [('Content-Type', 'text/plain'),
#                        ('Content-Length', str(len(output)))]
#    start_response(status, response_headers)
#    return [output]
