
from django.urls import path, re_path, include
from django.conf.urls import url
from main import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    re_path(r'^.*\.html', views.pages, name='pages'),

    path('', views.index, name='home'),
    path('new-position/', views.new_position, name='new_position'),
    url(r'^edit-position/(?P<pk>.*)$', views.edit_position, name='edit_position'),
    url(r'^active-position/(?P<pk>.*)$', views.active_position, name='active_position'),
    url(r'^del-position/(?P<pk>.*)$', views.del_position, name='del_position'),
    path('del-positions/', views.delete_positions, name='delete_positions'),
    # path('alert-off/', views.set_alert_off, name='set_alert_off'),
    # path('save-params/', views.save_params, name='save_params')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
