from django.conf.urls.defaults import *
from django.template import RequestContext
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


from SuryaWebPortal.views import home
from SuryaWebPortal.views import upload
from SuryaWebPortal.views.deployment import deployment
from SuryaWebPortal.views.debug import debug
from SuryaWebPortal.views import files
from SuryaWebPortal.views import result

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', home.home),
                       (r'^upload/$', upload.upload_image),

                       # For insertion into the email message
                       (r'^result/(\w*)/$', result.oneoffresult),

                       (r'^files/upload/(\w*)/$', files.uploadfile),
                       (r'^files/chart/(\w*)/$', files.chartfile),
                       (r'^files/debug/(\w*)/$', files.debugfile),

                       # !! debug output !!
                       (r'^debug/$', debug.debug),
                       (r'^debug/uploads/$', debug.uploads),
                       (r'^debug/uploads/(\w*)/$', debug.uploads),
                       (r'^debug/results/$', debug.results),
                       (r'^debug/failures/$', debug.failures),

                       # for admin 
                       (r'^admin/', include(admin.site.urls)),

                       # Data Login/Logout
                       (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
                       (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),
)
