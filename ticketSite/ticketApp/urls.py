from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ticket/<int:ticket_id>', views.ticket_by_id, name='ticket_by_id'),
    path('refresh_output/', views.refresh_output, name='refresh_output'),
]
