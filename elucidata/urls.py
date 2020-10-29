from django.conf.urls import url,include
from django.urls import path
from . import views
from .views import upload,operation1, operation2

urlpatterns = [
    path('', views.upload, name="upload"),
    url(r'^upload/$',upload),
    url(r'^(?P<filename>.*)/operation1/$',operation1),
    url(r'^(?P<filename>.*)/operation2/$',operation2),
]
