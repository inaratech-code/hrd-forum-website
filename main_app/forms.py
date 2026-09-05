from django import forms
from .models import Gallery, Resource, Incident, Membership

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'category', 'image', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': 'Enter photo title or event headline...'
            }),
            'category': forms.Select(choices=[
                ('Advocacy', 'Advocacy'),
                ('Fact-Finding', 'Fact-Finding'),
                ('Training', 'Training'),
                ('Assemblies', 'Assemblies'),
                ('General', 'General'),
            ], attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm bg-white'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'gallery-file-input',
                'accept': 'image/*'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': 'https://example.com/image.jpg (Optional URL fallback)'
            }),
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'category', 'format', 'file_size', 'file_upload', 'file_url', 'is_gated']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': 'Document title...'
            }),
            'category': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': 'Report, Guide, Policy...'
            }),
            'format': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': 'PDF, DOCX, ZIP...'
            }),
            'file_size': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': '2.5 MB'
            }),
            'file_upload': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm bg-white'
            }),
            'file_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm',
                'placeholder': 'https://...'
            }),
            'is_gated': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-teal-600 rounded border-slate-300 focus:ring-teal-500'
            })
        }
