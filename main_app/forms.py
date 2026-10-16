from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from .models import (
    Resource, Province, Membership, Incident, News,
    PopupConfig, Gallery, Blog, Video, TeamMember, 
    Collaboration, NewsFlash, SiteSettings, SupportContribution, ThematicSector
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
    category = forms.ChoiceField(
        choices=[
            ('', 'Select a category'),
            ('Report', 'Report'),
            ('Publication', 'Publication'),
            ('By-Laws', 'By-Laws'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
    )
    format = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'PDF'}),
    )
    file_size = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. 2.5 MB'}),
    )

    class Meta:
        model = Resource
        fields = ['title', 'category', 'format', 'file_size', 'cover_image', 'cover_image_url', 'file_upload', 'file_url', 'is_gated']
        labels = {
            'title': 'Resource / Publication Title',
            'category': 'Resource Category',
            'format': 'Document Format (e.g. PDF)',
            'file_size': 'File Size (e.g. 2.5 MB)',
            'cover_image': 'Cover Photo / Publication Thumbnail (Upload Image)',
            'cover_image_url': 'Cover Photo Web URL (Alternative)',
            'file_upload': 'Document File (PDF / DOCX)',
            'file_url': 'Document Download URL (Alternative)',
            'is_gated': 'Gated Access (Require user contact before downloading)'
        }
        help_texts = {
            'cover_image': 'Upload a cover photo, front page, or thumbnail for this publication/resource.',
            'cover_image_url': 'Or enter a direct image URL if hosted externally.',
            'file_upload': 'Upload the full document file (PDF, Word, etc.).',
            'file_url': 'Or provide an external link to access the publication.',
            'is_gated': 'When checked, visitors must submit their name and email to download.'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Annual Human Rights Protection Report 2026'}),
            'cover_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'resource-cover-input'}),
            'cover_image_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://example.com/cover-image.jpg'}),
            'file_upload': forms.FileInput(attrs={'class': FILE_CLASS, 'id': 'resource-file-input'}),
            'file_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://example.com/document.pdf'}),
            'is_gated': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_category = getattr(self.instance, 'category', '')
        if current_category and current_category not in self.fields['category'].choices:
            self.fields['category'].choices = [
                *self.fields['category'].choices,
                (current_category, f'{current_category} (existing category)'),
            ]


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
        fields = ['full_name', 'email', 'phone', 'province', 'joining_reason', 'status']
        labels = {
            'joining_reason': 'What is one specific reason you want to join HRD Forum and how can you support us?',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'your.email@example.com'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+977 9800000000'}),
            'province': forms.Select(attrs={'class': SELECT_CLASS}),
            'joining_reason': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'Explain your reason for joining and how you plan to support HRD Forum...'}),
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
        fields = ['title', 'subtitle', 'image', 'image_url', 'link_url', 'link_text', 'active']
        labels = {
            'title': 'Popup Title',
            'subtitle': 'Popup Text / Content',
            'image': 'Upload Photo / Image File',
            'image_url': 'Photo / Image URL (Alternative)',
            'link_url': 'Button Link URL',
            'link_text': 'Button Label',
            'active': 'Active (Show Popup on Website)',
        }
        help_texts = {
            'image': 'Upload a photo or banner image to display in the popup.',
            'image_url': 'Or enter a direct URL to an image (e.g. Unsplash, Cloudinary, etc.)',
            'subtitle': 'Announcement details or text description shown in the popup.',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g., National Human Rights Defenders Convention 2026'}),
            'subtitle': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Enter event details or announcement message...'}),
            'link_url': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://example.com or #'}),
            'link_text': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g., Register Online Now'}),
            'active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'popup-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://images.unsplash.com/...'}),
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
        fields = ['name', 'designation', 'category', 'bio', 'linkedin_url', 'order_index', 'image', 'image_url']
        labels = {
            'linkedin_url': 'LinkedIn Profile URL',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g., Jane Doe'}),
            'designation': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g., Senior Legal Advisor'}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'bio': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'linkedin_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://www.linkedin.com/in/username'}),
            'order_index': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'team-file-input'}),
            'image_url': forms.URLInput(attrs={'class': INPUT_CLASS}),
        }


class CollaborationForm(forms.ModelForm):
    class Meta:
        model = Collaboration
        fields = ['name', 'category', 'support_level', 'blurb', 'website_url', 'order_index', 'logo', 'logo_url']
        labels = {
            'support_level': 'Individual Supporter Recognition Level',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'category': forms.Select(attrs={'class': SELECT_CLASS}),
            'support_level': forms.Select(attrs={'class': SELECT_CLASS}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = self.instance.pk is None

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            candidate = User(username=self.cleaned_data.get('username', ''))
            validate_password(password, candidate)
        return password

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


class HomePageSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'hero_image', 'hero_image_url',
            'home_hero_badge', 'home_hero_title', 'home_hero_subtitle',
            'home_about_badge', 'home_about_title', 'home_about_text_1', 'home_about_text_2'
        ]
        labels = {
            'hero_image': 'Landing Page Hero Background Image (Upload)',
            'hero_image_url': 'Landing Page Hero Background Image URL (Alternative)',
            'home_hero_badge': 'Hero Section Top Tag / Badge',
            'home_hero_title': 'Hero Section Main Headline',
            'home_hero_subtitle': 'Hero Section Subtitle / Mission Summary',
            'home_about_badge': 'Overview Section Top Badge',
            'home_about_title': 'Overview Section Main Heading',
            'home_about_text_1': 'Overview Description Paragraph 1',
            'home_about_text_2': 'Overview Description Paragraph 2',
        }
        widgets = {
            'hero_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'home-hero-file'}),
            'hero_image_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://images.unsplash.com/...'}),
            'home_hero_badge': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'ESTABLISHED NATIONAL HUMAN RIGHTS COALITION'}),
            'home_hero_title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Protecting Rights & Empowering Defenders Across Nepal'}),
            'home_hero_subtitle': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Strengthening 7 provincial helpdesks...'}),
            'home_about_badge': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'ORGANIZATIONAL BACKGROUND'}),
            'home_about_title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'About HRD Forum Nepal'}),
            'home_about_text_1': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'home_about_text_2': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
        }


class AboutPageSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            # About Page - Hero & Showcase Photo
            'about_hero_badge', 'about_hero_title', 'about_hero_description',
            'about_image', 'about_image_url', 'about_image_caption', 'about_video_url',
            # About Page - Profile Section
            'profile_badge', 'profile_title', 'profile_text',
            'profile_feature_1_title', 'profile_feature_1_text',
            'profile_feature_2_title', 'profile_feature_2_text',
            # About Page - Mission & Vision
            'vision_title', 'vision_text', 'mission_title', 'mission_text',
            # Support Us & Bank Details
            'bank_qr_image', 'bank_name', 'bank_account_name', 'bank_account_no', 'bank_branch'
        ]
        labels = {
            'about_hero_badge': 'About Hero Top Badge (Small uppercase tag)',
            'about_hero_title': 'About Hero Main Heading (Blue Section)',
            'about_hero_description': 'About Hero Description (Lead text)',
            'about_image': 'About Hero Showcase Image (Direct Upload)',
            'about_image_url': 'About Hero Showcase Image URL (Alternative)',
            'about_image_caption': 'About Hero Image Card Caption',
            'about_video_url': 'About Hero Background Video URL (Optional)',
            'profile_badge': 'Profile Section Badge',
            'profile_title': 'Profile Section Title',
            'profile_text': 'Profile Section Main Story / Coalition Text',
            'profile_feature_1_title': 'Profile Pillar 1 Title',
            'profile_feature_1_text': 'Profile Pillar 1 Description',
            'profile_feature_2_title': 'Profile Pillar 2 Title',
            'profile_feature_2_text': 'Profile Pillar 2 Description',
            'vision_title': 'Vision Card Heading',
            'vision_text': 'Vision Statement',
            'mission_title': 'Mission Card Heading',
            'mission_text': 'Mission Statement',
            'bank_qr_image': 'Bank Payment QR Code (Upload Image)',
            'bank_name': 'Bank Name',
            'bank_account_name': 'Account Holder Name',
            'bank_account_no': 'Account Number',
            'bank_branch': 'Branch Name',
        }
        widgets = {
            'about_hero_badge': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'ABOUT HRD FORUM NEPAL'}),
            'about_hero_title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Protecting rights defenders and strengthening civic space across Nepal.'}),
            'about_hero_description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Coalition lead narrative...'}),
            'about_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'about-file-input'}),
            'about_image_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://images.unsplash.com/...'}),
            'about_image_caption': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'HRD Forum Nepal Field Network'}),
            'about_video_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://www.youtube.com/embed/... or direct video URL'}),
            'profile_badge': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Coalition Profile'}),
            'profile_title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Profile of HRD Forum Nepal'}),
            'profile_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'profile_feature_1_title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'profile_feature_1_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'profile_feature_2_title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'profile_feature_2_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'vision_title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'vision_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'mission_title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'mission_text': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
            'bank_qr_image': forms.FileInput(attrs={'class': FILE_CLASS, 'accept': 'image/*', 'id': 'qr-file-input'}),
            'bank_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'bank_account_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'bank_account_no': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'bank_branch': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }


# Compatibility alias
SiteSettingsForm = AboutPageSettingsForm


class ThematicSectorForm(forms.ModelForm):
    class Meta:
        model = ThematicSector
        fields = ['title', 'description', 'icon', 'order_index']
        labels = {
            'title': 'Thematic Sector Title',
            'description': 'Description & Scope of Protection',
            'icon': 'FontAwesome Icon Class (e.g. fa-solid fa-gavel)',
            'order_index': 'Display Order Index',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Legal Defense & Rapid Support'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Description...'}),
            'icon': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'fa-solid fa-gavel'}),
            'order_index': forms.NumberInput(attrs={'class': INPUT_CLASS}),
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
