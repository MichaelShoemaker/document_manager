from django.db import models
import os

class Document(models.Model):
    uid = models.CharField(max_length=100)
    ssn = models.CharField(max_length=11)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.document_type}"

    def filename(self):
        return os.path.basename(self.file.name)
