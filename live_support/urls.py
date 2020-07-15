# live_support/urls.py
from . import views
from chat.views import *
from django.contrib import admin
from rest_framework import routers
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

router = routers.DefaultRouter()
router.register('operator', OperatorViewSets, basename='operator')
router.register('session', SessionViewSets, basename='session')

urlpatterns = [
    path('api/operator/status/', OperatorViewSets.as_view({'get': 'status'})),
    path('api/operator/<name>/',
         OperatorViewSets.as_view({'get': 'get_by_username', 'patch': 'patch', 'delete': 'destroy'})),
    path('api/', include(router.urls)),
]

urlpatterns += i18n_patterns(
    path('admin/start_support/', views.start_support, name='start_support'),
    path('admin/stop_support/', views.stop_support, name='stop_support'),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
)
