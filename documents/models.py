from django.db import models
import os
from django.conf import settings

def document_upload_path(instance, filename):
    # Create a path based on the UID
    # Format: documents/{uid}/{filename}
    return os.path.join('documents', instance.uid, filename)

class Document(models.Model):
    uid = models.CharField(max_length=100)
    ssn = models.CharField(max_length=11)  # Can store both formats: 9 digits or XXX-XX-XXXX
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.document_type}"

    def filename(self):
        return os.path.basename(self.file.name)
        
    def save(self, *args, **kwargs):
        # Ensure the directory exists before saving
        if self.file:
            # Get the directory path
            directory = os.path.join(settings.MEDIA_ROOT, 'documents', self.uid)
            # Create the directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
        super().save(*args, **kwargs)
