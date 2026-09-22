from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group
from .models import (
    Resource, Province, Membership, Incident, News,
    PopupConfig, Gallery, Blog, Video, TeamMember, 
    Collaboration, NewsFlash, SiteSettings, SupportContribution
)

# HELPER INPUT STYLES
INPUT_CLASS = "w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm bg-white"
PASSWORD_INPUT_CLASS = INPUT_CLASS + " pr-12"
TEXTAREA_CLASS = "w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm bg-white rows-4"
SELECT_CLASS = "w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm bg-white"
CHECKBOX_CLASS = "w-5 h-5 text-teal-600 rounded border-slate-300 focus:ring-teal-500"
FILE_CLASS = "w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none transition text-slate-800 font-medium text-sm bg-white"


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'category', 'image', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Enter photo title or event headline...'}),
            'category': forms.Select(choices=[
                ('Advocacy', 'Advocacy'),
                ('Fact-Finding', 'Fact-Finding'),
                ('Training', 'Training'),
                ('Assemblies', 'Assemblies'),
                ('General', 'General'),
            ], attrs={'class': SELECT_CLASS}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'gallery-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://example.com/image.jpg (Optional URL fallback)'}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'category', 'file_upload', 'file_url', 'is_gated']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Document title...'}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'file_upload': forms.FileInput(attrs={'class': FILE_CLASS, 'id': 'resource-file-input'}),
            'file_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://...'}),
            'is_gated': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'category', 'published_date', 'summary', 'content', 'image', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'News title...'}),
            'category': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'News & Updates, Press Release...'}),
            'published_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'summary': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Short brief summary...'}),
            'content': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 6, 'placeholder': 'Full article body...'}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'news-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://...'}),
        }


class OrganizationalUpdateForm(forms.ModelForm):
    class Meta:
        from .models import OrganizationalUpdate
        model = OrganizationalUpdate
        fields = ['title', 'date_posted', 'description', 'is_urgent', 'document_attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Update title...'}),
            'date_posted': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'Full details...'}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-cobalt-accent'}),
            'document_attachment': forms.FileInput(attrs={'class': FILE_CLASS}),
        }


class ProvinceForm(forms.ModelForm):
    class Meta:
        model = Province
        fields = ['name', 'code', 'base_city', 'coords_lat', 'coords_lng', 'coordinators_count', 'districts_count', 'helpline_phone', 'address', 'helpdesk_email', 'active_cases', 'description', 'long_summary']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Bagmati Province'}),
            'code': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'P3'}),
            'base_city': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Kathmandu'}),
            'coords_lat': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': 'any'}),
            'coords_lng': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': 'any'}),
            'coordinators_count': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'districts_count': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'helpline_phone': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'address': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'helpdesk_email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'active_cases': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'long_summary': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 5}),
        }


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['full_name', 'email', 'phone', 'province', 'organization', 'role', 'status']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'province': forms.Select(attrs={'class': SELECT_CLASS}),
            'organization': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'role': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
        }


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['reporter_name', 'contact_info', 'province', 'incident_type', 'priority', 'details']
        widgets = {
            'reporter_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'contact_info': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'province': forms.Select(attrs={'class': SELECT_CLASS}),
            'incident_type': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'priority': forms.Select(choices=[
                ('Low', 'Low'),
                ('Medium', 'Medium'),
                ('High', 'High'),
                ('Urgent', 'Urgent'),
            ], attrs={'class': SELECT_CLASS}),
            'details': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
        }


class PopupConfigForm(forms.ModelForm):
    class Meta:
        model = PopupConfig
        fields = ['title', 'subtitle', 'link_url', 'link_text', 'active', 'image', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'subtitle': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2}),
            'link_url': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'link_text': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'popup-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
        }


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'author', 'published_date', 'content', 'image', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'author': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'published_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'content': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 6}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'blog-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'embed_url', 'category', 'published_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'embed_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://www.youtube.com/embed/...'}),
            'category': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'published_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'designation', 'category', 'bio', 'order_index', 'image', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'designation': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'bio': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'order_index': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'team-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
        }


class CollaborationForm(forms.ModelForm):
    class Meta:
        model = Collaboration
        fields = ['name', 'category', 'blurb', 'website_url', 'order_index', 'logo', 'logo_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'blurb': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'website_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
            'order_index': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'logo': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'collab-file-input'}),
            'logo_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
        }


class NewsFlashForm(forms.ModelForm):
    class Meta:
        model = NewsFlash
        fields = ['text', 'link_url', 'active', 'order_index']
        widgets = {
            'text': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'link_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
            'active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'order_index': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': PASSWORD_INPUT_CLASS,
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
        required=False,
        help_text='Leave blank to keep the current password when editing.',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'is_staff': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_superuser': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
            self.save_m2m()
        return user


class PortalPasswordChangeForm(PasswordChangeForm):
    """Styled password change form for portal settings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_attrs = {
            'old_password': ('Current password', 'Enter your current password...'),
            'new_password1': ('New password', 'Enter a new password...'),
            'new_password2': ('Confirm new password', 'Re-enter the new password...'),
        }
        for name, (label, placeholder) in field_attrs.items():
            self.fields[name].label = label
            self.fields[name].widget.attrs.update({
                'class': PASSWORD_INPUT_CLASS,
                'placeholder': placeholder,
            })


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Group / Role Name'}),
        }


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'vision_text', 'mission_text', 
            'hero_image', 'bank_qr_image',
            'bank_name', 'bank_account_name', 'bank_account_no', 'bank_branch'
        ]
        widgets = {
            'vision_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'mission_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'hero_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'hero-file-input'}),
            'bank_qr_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'qr-file-input'}),
            'bank_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'bank_account_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'bank_account_no': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'bank_branch': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }

class SupportContributionForm(forms.ModelForm):
    class Meta:
        model = SupportContribution
        fields = ['name', 'phone', 'email', 'receipt_image', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email Address'}),
            'receipt_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Any additional notes...'}),
        }
