from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat_api'),
    path('summarize/', TextSummaryAPIView.as_view(), name='summarize'),
]
