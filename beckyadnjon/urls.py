from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^rsvp/", include("rsvp.urls"))
)

urlpatterns+=patterns('django.views.generic.simple',(r'^wheretostay/', 'direct_to_template', {'template': 'wheretostay.html'}),)
urlpatterns+=patterns('django.views.generic.simple',(r'^ontheday/', 'direct_to_template', {'template': 'ontheday.html'}),)
urlpatterns+=patterns('django.views.generic.simple',(r'^thingstodo/', 'direct_to_template', {'template': 'thingstodo.html'}),)
urlpatterns+=patterns('django.views.generic.simple',(r'^other/', 'direct_to_template', {'template': 'other.html'}),)




if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
