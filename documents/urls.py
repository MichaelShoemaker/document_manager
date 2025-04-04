from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_document, name='upload_document'),
    path('search/', views.search_documents, name='search_documents'),
    path('verify/<uuid:document_id>/', views.verify_document, name='verify_document'),
    path('reject/<uuid:document_id>/', views.reject_document, name='reject_document'),
] 