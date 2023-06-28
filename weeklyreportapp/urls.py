from django.urls import path

from . import views

app_name = "weeklyreportapp"
urlpatterns = [
    path("", views.index, name="weeklyreportapp"),
]
