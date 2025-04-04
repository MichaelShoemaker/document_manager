from django.db import models
import os
from django.conf import settings
import uuid
from django.contrib.auth.models import User
import hashlib

def calculate_file_hash(file):
    """Calculate SHA-256 hash of an uploaded file."""
    sha256_hash = hashlib.sha256()
    for chunk in file.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def document_upload_path(instance, filename):
    """
    Generate file path: documents/{member_uid}/{document_type}/{filename}
    """
    document = instance.document
    return os.path.join(
        'documents',
        document.member.uid,
        document.document_type.name.lower().replace(' ', '_'),
        filename
    )

class Member(models.Model):
    uid = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    ssn = models.CharField(max_length=11)  # Can store both formats: 9 digits or XXX-XX-XXXX
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.uid})"

    class Meta:
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['ssn']),
            models.Index(fields=['last_name', 'first_name']),
        ]

class Dependent(models.Model):
    RELATIONSHIP_CHOICES = [
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('OTHER', 'Other'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='dependents')
    uid = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.relationship} of {self.member.uid})"

    class Meta:
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['member', 'relationship']),
        ]

class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    dependent = models.ForeignKey(Dependent, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    uploader = models.ForeignKey(User, on_delete=models.PROTECT)
    upload_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        subject = self.dependent if self.dependent else self.member
        return f"{self.document_type.name} - {subject}"

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['document_type', 'member']),
            models.Index(fields=['upload_date']),
        ]

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=64)  # SHA-256 hash
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.file_hash and self.file:
            self.file_hash = calculate_file_hash(self.file)
        if not self.file_size and self.file:
            self.file_size = self.file.size
        if not self.original_filename and self.file:
            self.original_filename = self.file.name

        # Ensure the directory exists before saving
        if self.file:
            directory = os.path.dirname(os.path.join(settings.MEDIA_ROOT, self.file.name))
            os.makedirs(directory, exist_ok=True)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_filename} ({self.document.document_type.name})"

    class Meta:
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['uploaded_at']),
        ]

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', 'Document Uploaded'),
        ('VERIFY', 'Document Verified'),
        ('REJECT', 'Document Rejected'),
        ('DELETE', 'Document Deleted'),
        ('UPDATE', 'Document Updated'),
        ('VIEW', 'Document Viewed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    previous_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} - {self.document} by {self.user}"

    class Meta:
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['document', 'action']),
        ]
