from django.urls import path
from .views import NextTrackingNumberView

urlpatterns = [
    path('',NextTrackingNumberView.as_view(),name='tracking-number-view'),
    ]
