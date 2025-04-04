from django import forms
from .models import Member, Dependent, Document, File, DocumentType

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['uid', 'ssn', 'first_name', 'last_name', 'date_of_birth']
        widgets = {
            'uid': forms.TextInput(attrs={'class': 'form-control'}),
            'ssn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX-XX-XXXX or XXXXXXXXX',
                'title': 'Enter SSN with or without dashes'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class DependentForm(forms.ModelForm):
    class Meta:
        model = Dependent
        fields = ['uid', 'first_name', 'last_name', 'relationship', 'date_of_birth']
        widgets = {
            'uid': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
        'style': 'display: none;'
    }))
    
    class Meta:
        model = Document
        fields = ['document_type', 'member', 'dependent', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'member': forms.Select(attrs={'class': 'form-control'}),
            'dependent': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dependent'].required = False
        self.fields['notes'].required = False

    def save(self, commit=True):
        document = super().save(commit=False)
        if commit:
            document.save()
            
            # Create File instance
            if self.cleaned_data.get('file'):
                uploaded_file = self.cleaned_data['file']
                File.objects.create(
                    document=document,
                    file=uploaded_file,
                    original_filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    mime_type=uploaded_file.content_type
                )
        return document

    def clean_ssn(self):
        ssn = self.cleaned_data.get('ssn', '')
        if not ssn:
            return ssn
            
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, ssn))
        
        # Validate length
        if len(digits) != 9:
            raise forms.ValidationError("SSN must be exactly 9 digits")
            
        # Return the original format if it was entered with dashes, otherwise return just digits
        if '-' in ssn:
            return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
        return digits

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file and 'file' not in self.files:
            raise forms.ValidationError("Please select a file to upload")
        return file

    def clean(self):
        cleaned_data = super().clean()
        print("Form data:", self.data)  # Debug info
        print("Files:", self.files)  # Debug info
        print("Cleaned data:", cleaned_data)  # Debug info
        return cleaned_data 