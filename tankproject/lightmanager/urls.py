from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "<int:channel_id>/<int:milli_percent>",
        views.set_brightness,
        name="set_brightness",
    ),
    re_path("^sbs/.*", views.set_brightnesses, name="set_brightnesses"),
    re_path("^warmer/.*", views.warmer, name="warmer"),
    re_path("^cooler/.*", views.cooler, name="cooler"),
]
