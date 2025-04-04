from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_document, name='upload_document'),
    path('search/', views.search_documents, name='search_documents'),
] 