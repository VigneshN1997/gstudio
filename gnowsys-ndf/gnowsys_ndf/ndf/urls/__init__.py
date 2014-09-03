from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls import *
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from gnowsys_ndf.ndf.views.email_registration import password_reset_email,password_reset_error

from registration.backends.default.views import RegistrationView

from gnowsys_ndf.ndf.forms import *
from gnowsys_ndf.ndf.views.home import HomeRedirectView, homepage
from gnowsys_ndf.ndf.views.methods import tag_info
from gnowsys_ndf.ndf.views.custom_app_view import custom_app_view, custom_app_new_view
admin.autodiscover()

urlpatterns = patterns('',
    (r'^online/', include('online_status.urls')),   #for online_users 
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^pref_lang/$', include('gnowsys_ndf.ndf.urls.languagepref')),
    (r'^admin/data/', include('gnowsys_ndf.ndf.urls.adminDashboard')),
    (r'^admin/designer/', include('gnowsys_ndf.ndf.urls.adminDesignerDashboard')),
    (r'^raw/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.raw'),
    (r'^r/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.raw'),
    (r'^m/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.html'),
    (r'^t/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.text'),
    (r'^new/$', 'gnowsys_ndf.mobwrite.views.new'),
    (r'^mobwrite/', 'gnowsys_ndf.mobwrite.views.mobwrite'),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', HomeRedirectView.as_view()),        

    (r'^(?P<group_id>[^/]+)/file', include('gnowsys_ndf.ndf.urls.file')),
    (r'^(?P<group_id>[^/]+)/image', include('gnowsys_ndf.ndf.urls.image')),
    (r'^(?P<group_id>[^/]+)/video', include('gnowsys_ndf.ndf.urls.video')),
    (r'^(?P<group_id>[^/]+)/page', include('gnowsys_ndf.ndf.urls.page')),
    (r'^(?P<group_id>[^/]+)/group', include('gnowsys_ndf.ndf.urls.group')),
    (r'^(?P<group_id>[^/]+)/forum', include('gnowsys_ndf.ndf.urls.forum')),
    (r'^(?P<group_id>[^/]+)/quiz', include('gnowsys_ndf.ndf.urls.quiz')),
    (r'^(?P<group_id>[^/]+)/course', include('gnowsys_ndf.ndf.urls.course')),
    (r'^(?P<group_id>[^/]+)/module', include('gnowsys_ndf.ndf.urls.module')),
    (r'^(?P<group_id>[^/]+)/search', include('gnowsys_ndf.ndf.urls.search_urls')),
    (r'^(?P<group_name>[^/]+)/task', include('gnowsys_ndf.ndf.urls.task')),
    (r'^(?P<group_id>[^/]+)/batch', include('gnowsys_ndf.ndf.urls.batch')),
    (r'^(?P<group_id>[^/]+)/ajax/', include('gnowsys_ndf.ndf.urls.ajax-urls')),
    (r'^(?P<group_id>[^/]+)/search/', include('gnowsys_ndf.ndf.urls.search_urls')),	
    (r'^(?P<group_id>[^/]+)/wikidata', include('gnowsys_ndf.ndf.urls.wikidata')),
    (r'^(?P<group_id>[^/]+)/', include('gnowsys_ndf.ndf.urls.user')),
    (r'^(?P<group_id>[^/]+)/ratings', include('gnowsys_ndf.ndf.urls.ratings')),                     
    
    
    (r'^(?P<group_id>[^/]+)/browse topic', include('gnowsys_ndf.ndf.urls.browse_topic')),
    url(r'^(?P<group_id>[^/]+)/topic_details/(?P<app_Id>[\w-]+)', 'gnowsys_ndf.ndf.views.browse_topic.topic_detail_view', name='topic_details'),

    (r'^(?P<group_id>[^/]+)/browse resource', include('gnowsys_ndf.ndf.urls.browse_resource')),
    
    (r'^(?P<group_id>[^/]+)/mis', include('gnowsys_ndf.ndf.urls.mis', namespace='mis'), {'app_name': "MIS"}),
    (r'^(?P<group_id>[^/]+)/mis-po', include('gnowsys_ndf.ndf.urls.mis', namespace='mis-po'), {'app_name': "MIS-PO"}),
    url(r'^(?P<group_id>[^/]+)/inviteusers/(?P<meetingid>[^/]+)','gnowsys_ndf.ndf.views.meeting.invite_meeting', name='invite_meeting'),
	url(r'^(?P<group_id>[^/]+)/meeting/(?P<meetingid>[^/]+)','gnowsys_ndf.ndf.views.meeting.output', name='newmeeting'), 
    url(r'^(?P<group_id>[^/]+)/meeting','gnowsys_ndf.ndf.views.meeting.dashb', name='Meeting'),                  ########## meeting app
    url(r'^(?P<group_id>[^/]+)/online','gnowsys_ndf.ndf.views.meeting.get_online_users', name='get_online_users'),                  ########## meeting app
    
    
    
    
   #url(r'^(?P<group_id>[^/]+)/online','gnowsys_ndf.ndf.views.online.tests', name='Online'),                     ########## online app  

    (r'^(?P<group_id>[^/]+)/observation', include('gnowsys_ndf.ndf.urls.observation')),
    (r'^(?P<group_id>[^/]+)/Observations', include('gnowsys_ndf.ndf.urls.observation')),

    url(r'^(?P<group_id>[^/]+)/(?P<node_id>[^/]+)/create_discussion$', 'gnowsys_ndf.ndf.views.methods.create_discussion', name='create_discussion'),    
    url(r'^(?P<group_id>[^/]+)/discussion_reply$', 'gnowsys_ndf.ndf.views.methods.discussion_reply', name='discussion_reply'),    

    #url(r'^(?P<group_id>[^/]+)/visualize', 'gnowsys_ndf.ndf.views.visualize.graphs', name='visualize'),
    url(r'^(?P<group_id>[^/]+)/visualize', include('gnowsys_ndf.ndf.urls.visualise_urls')),
    
    url(r'^(?P<group_id>[^/]+)/$', 'gnowsys_ndf.ndf.views.group.group_dashboard', name='groupchange'),    
    #(r'^(?P<group_id>[^/]+)/', include('gnowsys_ndf.ndf.urls.group')),
    url(r'^(?P<group_id>[^/]+)/annotationlibInSelText$', 'gnowsys_ndf.ndf.views.ajax_views.annotationlibInSelText', name='annotationlibInSelText'),
    url(r'^(?P<group_id>[^/]+)/delComment$', 'gnowsys_ndf.ndf.views.ajax_views.delComment', name='delComment'),
    url(r'^(?P<group_id>[^/]+)/tags/(?P<tagname>[^/]+)$','gnowsys_ndf.ndf.views.methods.tag_info', name='tag_info'),

    
   

    (r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)', include('gnowsys_ndf.ndf.urls.custom_app')),    
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)$', custom_app_view, name='GAPPS'),       
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', custom_app_view, name='GAPPS_set'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', custom_app_view, name='GAPPS_set_instance'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)/edit/$', custom_app_new_view, name='GAPPS_set_instance_edit'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/new/$', custom_app_new_view, name='GAPPS_set_new_instance'),
    
    # (r'^home','gnowsys_ndf.ndf.views.group.group_dashboard'),
    # (r'^home/', 'gnowsys_ndf.ndf.views.home.homepage'),
    
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),

    
    url(r'^accounts/password/change/done/', auth_views.password_change_done, name='password_change_done'),
    url(r'^accounts/password/change/', auth_views.password_change, {'password_change_form': UserChangeform}),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'set_password_form': UserResetform},name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/done/$',auth_views.password_reset_done,name="password_reset_done"),
    url(r'^accounts/password/reset/error/$', password_reset_error , name='password_reset_error'),
    url(r'^accounts/password/reset/$',
        password_reset_email,
        {
            'template_name': 'registration/password_reset_form.html',
            'email_template_name': 'registration/password_reset_email.html',
            'subject_template_name':'registration/password_reset_email_subject.txt'
        },
        name='password_reset'
    ),
    
     (r'^accounts/', include('registration_email.backends.default.urls')),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegistrationForm)),
   
    url(r'^Beta/', TemplateView.as_view(template_name= 'gstudio/beta.html'), name="beta"),
)
