from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import MemberForm, DependentForm, DocumentUploadForm
from .models import Member, Dependent, Document, File, DocumentType, AuditLog

# Create your views here.

@login_required
def upload_document(request):
    if request.method == 'POST':
        # Handle member creation/selection
        member_form = MemberForm(request.POST, prefix='member')
        document_form = DocumentUploadForm(request.POST, request.FILES)
        
        if member_form.is_valid() and document_form.is_valid():
            try:
                # Get or create member
                member, created = Member.objects.get_or_create(
                    uid=member_form.cleaned_data['uid'],
                    defaults=member_form.cleaned_data
                )
                if not created:
                    # Update existing member's information
                    for field, value in member_form.cleaned_data.items():
                        setattr(member, field, value)
                    member.save()

                # Create document
                document = document_form.save(commit=False)
                document.member = member
                document.uploader = request.user
                document.save()

                # Create audit log entry
                AuditLog.objects.create(
                    document=document,
                    action='UPLOAD',
                    user=request.user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    new_status='PENDING'
                )

                messages.success(request, 'Document uploaded successfully!')
                return redirect('search_documents')
            except Exception as e:
                messages.error(request, f'Error saving document: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        member_form = MemberForm(prefix='member')
        document_form = DocumentUploadForm()
    
    return render(request, 'documents/upload.html', {
        'member_form': member_form,
        'document_form': document_form,
        'document_types': DocumentType.objects.all()
    })

@login_required
def search_documents(request):
    query = request.GET.get('q', '')
    documents = []
    
    if query:
        # Search in Member fields
        member_matches = Member.objects.filter(
            Q(uid__icontains=query) |
            Q(ssn__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
        # Search in Document and related fields
        documents = Document.objects.filter(
            Q(member__in=member_matches) |
            Q(document_type__name__icontains=query) |
            Q(dependent__first_name__icontains=query) |
            Q(dependent__last_name__icontains=query) |
            Q(notes__icontains=query)
        ).select_related('member', 'dependent', 'document_type')
        
        # Log document views
        for doc in documents:
            AuditLog.objects.create(
                document=doc,
                action='VIEW',
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
    
    return render(request, 'documents/search.html', {
        'documents': documents,
        'query': query
    })

@login_required
def verify_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    previous_status = document.status
    document.status = 'VERIFIED'
    document.save()
    
    # Create audit log entry
    AuditLog.objects.create(
        document=document,
        action='VERIFY',
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        previous_status=previous_status,
        new_status='VERIFIED'
    )
    
    messages.success(request, 'Document verified successfully!')
    return redirect('search_documents')

@login_required
def reject_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    previous_status = document.status
    document.status = 'REJECTED'
    document.save()
    
    # Create audit log entry
    AuditLog.objects.create(
        document=document,
        action='REJECT',
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        previous_status=previous_status,
        new_status='REJECTED',
        comment=request.POST.get('rejection_reason', '')
    )
    
    messages.warning(request, 'Document rejected.')
    return redirect('search_documents')
