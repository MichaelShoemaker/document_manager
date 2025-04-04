from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .forms import DocumentForm
from .models import Document
from django.db.models import Q

# Create your views here.

def upload_document(request):
    if request.method == 'POST':
        print("Files in request:", request.FILES)  # Debug information
        form = DocumentForm(request.POST, request.FILES)
        print("Form is valid:", form.is_valid())  # Debug information
        if form.is_valid():
            try:
                document = form.save()
                messages.success(request, 'Document uploaded successfully!')
                return redirect('search_documents')
            except Exception as e:
                print("Error saving document:", str(e))  # Debug information
                messages.error(request, f'Error saving document: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            print("Form errors:", form.errors)  # Debug information
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = DocumentForm()
    
    return render(request, 'documents/upload.html', {'form': form})

def search_documents(request):
    query = request.GET.get('q', '')
    documents = []
    
    if query:
        documents = Document.objects.filter(
            Q(uid__icontains=query) |
            Q(ssn__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(document_type__icontains=query)
        )
    
    return render(request, 'documents/search.html', {
        'documents': documents,
        'query': query
    })
