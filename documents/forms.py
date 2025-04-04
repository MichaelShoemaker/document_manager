from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['uid', 'ssn', 'first_name', 'last_name', 'document_type', 'file']
        widgets = {
            'uid': forms.TextInput(attrs={'class': 'form-control'}),
            'ssn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX-XX-XXXX or XXXXXXXXX',
                'title': 'Enter SSN with or without dashes'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'style': 'display: none;'}),
        }

    def clean_ssn(self):
        ssn = self.cleaned_data.get('ssn', '')
        if not ssn:
            return ssn
            
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, ssn))
        
        # Pad with zeros if less than 9 digits
        digits = digits.zfill(9)
        
        # Format as XXX-XX-XXXX
        formatted_ssn = f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
        return formatted_ssn

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