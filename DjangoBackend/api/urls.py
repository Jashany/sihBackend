from django.urls import path
from .views import *

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat_api'),
    path('summarize/', TextSummaryAPIView.as_view(), name='summarize'),
    path('judgement/', StringProcessingView.as_view(), name='process_string'),
    path('lsi/', LSIView.as_view(), name='lsi')
]
