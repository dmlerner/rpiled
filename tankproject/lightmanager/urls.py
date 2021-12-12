from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:channel_id>/<int:milli_percent>', views.set_brightness, name='set_brightness'),
]
