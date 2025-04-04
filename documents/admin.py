from django.contrib import admin
from .models import Member, Dependent, Document, DocumentType, File, AuditLog

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('uid', 'first_name', 'last_name', 'ssn', 'date_of_birth')
    search_fields = ('uid', 'first_name', 'last_name', 'ssn')
    list_filter = ('date_of_birth',)

@admin.register(Dependent)
class DependentAdmin(admin.ModelAdmin):
    list_display = ('uid', 'first_name', 'last_name', 'relationship', 'member', 'date_of_birth')
    search_fields = ('uid', 'first_name', 'last_name')
    list_filter = ('relationship', 'date_of_birth')

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_type', 'member', 'dependent', 'status', 'upload_date')
    list_filter = ('status', 'document_type', 'upload_date')
    search_fields = ('member__uid', 'member__first_name', 'member__last_name', 'dependent__first_name', 'dependent__last_name')
    date_hierarchy = 'upload_date'

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'original_filename', 'file_size', 'mime_type', 'uploaded_at')
    search_fields = ('original_filename', 'file_hash')
    list_filter = ('mime_type', 'uploaded_at')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'action', 'user', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('document__id', 'user__username', 'ip_address', 'comment')
    date_hierarchy = 'timestamp'
    readonly_fields = ('document', 'action', 'user', 'timestamp', 'ip_address', 'user_agent', 'previous_status', 'new_status', 'comment')
