from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin import ModelAdmin, TabularInline
from django.core.exceptions import ValidationError
from django.utils.html import mark_safe, escape

from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Video, GatedDownloadLead,
    TeamMember, Collaboration, NewsFlash, UniqueVisitor,
    SiteSettings, ThematicSector
)
from .security import EXPOSED_LEGACY_ADMIN_PASSWORD


class SecureAdminAuthenticationForm(AdminAuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.check_password(EXPOSED_LEGACY_ADMIN_PASSWORD):
            raise ValidationError(
                'This account uses an exposed legacy password. Reset it before signing in.',
                code='exposed_legacy_password',
            )


admin.site.login_form = SecureAdminAuthenticationForm


@admin.register(Stats)
class StatsAdmin(ModelAdmin):
    list_display = ('provincial_networks', 'monitored_defenders', 'resolved_cases', 'total_visitors')


@admin.register(Province)
class ProvinceAdmin(ModelAdmin):
    list_display = ('name', 'code', 'base_city', 'helpdesk_email', 'coordinators_count', 'helpline_phone', 'active_cases')
    list_display_links = ('name',)
    search_fields = ('name', 'code', 'base_city', 'helpdesk_email', 'address')
    list_filter = ('base_city',)


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'category', 'published_date')
    list_display_links = ('title', 'thumbnail_preview')
    search_fields = ('title', 'summary', 'content')
    list_filter = ('category', 'published_date')
    date_hierarchy = 'published_date'

    def thumbnail_preview(self, obj):
        img = obj.display_image
        if img:
            return mark_safe(f'<img src="{img}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 6px;" />')
        return "-"
    thumbnail_preview.short_description = "Thumbnail"


class GatedDownloadLeadInline(TabularInline):
    model = GatedDownloadLead
    extra = 0
    readonly_fields = ('user_name', 'user_email', 'downloaded_at')
    can_delete = False


@admin.register(Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ('cover_preview', 'title', 'category', 'format', 'file_size', 'is_gated')
    list_display_links = ('title', 'cover_preview')
    search_fields = ('title',)
    list_filter = ('category', 'format', 'is_gated')
    inlines = [GatedDownloadLeadInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'category', 'format', 'file_size', 'is_gated')
        }),
        ('Cover Photo / Thumbnail', {
            'fields': ('cover_image', 'cover_image_url', 'cover_preview_detail'),
            'description': 'Upload a cover photo or thumbnail for this publication or resource (e.g. document cover page, book cover).'
        }),
        ('Publication Document / File', {
            'fields': ('file_upload', 'file_url'),
            'description': 'Upload the document file directly (PDF, DOCX) or specify an external download URL.'
        }),
    )
    readonly_fields = ('cover_preview_detail',)

    def cover_preview(self, obj):
        img = obj.display_cover
        if img:
            return mark_safe(f'<img src="{img}" style="width: 48px; height: 64px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.12);" />')
        return mark_safe('<span style="color: #94a3b8; font-size: 11px;">No cover</span>')
    cover_preview.short_description = "Cover Photo"

    def cover_preview_detail(self, obj):
        img = obj.display_cover
        if img:
            return mark_safe(f'<img src="{img}" style="max-width: 200px; max-height: 260px; object-fit: cover; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />')
        return mark_safe('<span style="color: #94a3b8; font-size: 12px;">No cover photo uploaded yet. Choose an image file above or provide an image URL.</span>')
    cover_preview_detail.short_description = "Current Cover Photo"


@admin.register(Membership)
class MembershipAdmin(ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'province', 'status_badge', 'created_at')
    list_display_links = ('full_name',)
    search_fields = ('full_name', 'email', 'province__name', 'joining_reason')
    list_filter = ('status', 'province', 'created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def status_badge(self, obj):
        status_styles = {
            'approved': 'background-color: #0f766e; color: #ffffff;',
            'pending': 'background-color: #d97706; color: #ffffff;',
            'rejected': 'background-color: #dc2626; color: #ffffff;',
        }
        st = obj.status or 'pending'
        style = status_styles.get(st.lower(), 'background-color: #64748b; color: #ffffff;')
        return mark_safe(f'<span class="badge" style="{style} font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 12px; display: inline-block;">{st.title()}</span>')
    status_badge.short_description = "Status"


@admin.register(Incident)
class IncidentAdmin(ModelAdmin):
    list_display = ('reporter_name', 'province', 'incident_type', 'priority_badge', 'contact_info', 'created_at')
    list_display_links = ('reporter_name',)
    search_fields = ('reporter_name', 'contact_info', 'province__name', 'details')
    list_filter = ('province', 'incident_type', 'priority', 'created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def priority_badge(self, obj):
        prio_styles = {
            'Urgent': 'background-color: #dc2626; color: #ffffff;',
            'High': 'background-color: #ea580c; color: #ffffff;',
            'Medium': 'background-color: #d97706; color: #ffffff;',
            'Low': 'background-color: #2563eb; color: #ffffff;',
        }
        prio = getattr(obj, 'priority', 'High') or 'High'
        style = prio_styles.get(prio, 'background-color: #dc2626; color: #ffffff;')
        return mark_safe(f'<span class="badge" style="{style} font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 12px; display: inline-block;">{prio}</span>')
    priority_badge.short_description = "Priority"


@admin.register(PopupConfig)
class PopupConfigAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'active', 'link_text', 'link_url')
    list_display_links = ('title', 'thumbnail_preview')
    list_editable = ('active',)
    fields = ('title', 'subtitle', 'image', 'photo_preview', 'image_url', 'link_url', 'link_text', 'active')
    readonly_fields = ('photo_preview',)

    def thumbnail_preview(self, obj):
        img = obj.display_image
        if img:
            return mark_safe(f'<img src="{img}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 6px;" />')
        return "-"
    thumbnail_preview.short_description = "Photo"

    def photo_preview(self, obj):
        img = obj.display_image if obj else None
        if img:
            return mark_safe(f'<img src="{img}" style="max-width: 320px; max-height: 220px; border-radius: 8px; border: 1px solid #ddd; object-fit: cover;" />')
        return "No photo uploaded or linked"
    photo_preview.short_description = "Photo Preview"


@admin.register(Gallery)
class GalleryAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'clickable_title', 'category_badge', 'created_at')
    list_display_links = ('clickable_title', 'thumbnail_preview')
    list_filter = ('category', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'preview_image')

    def thumbnail_preview(self, obj):
        img = obj.display_image
        if img:
            return mark_safe(f'<img src="{escape(img)}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 6px; border: 1px solid #cbd5e1;" />')
        return "-"
    thumbnail_preview.short_description = "Thumbnail"

    def clickable_title(self, obj):
        return mark_safe(f'<strong style="color: #0f766e; font-weight: 700;">{escape(obj.title)}</strong>')
    clickable_title.short_description = "Title"

    def category_badge(self, obj):
        cat = obj.category or 'General'
        return mark_safe(f'<span class="badge" style="background-color: #0f766e; color: #ffffff; padding: 5px 12px; border-radius: 12px; font-weight: 700;">{escape(cat)}</span>')
    category_badge.short_description = "Category"

    def preview_image(self, obj):
        img = obj.display_image
        if img:
            return mark_safe(f'<img src="{escape(img)}" style="max-width: 320px; max-height: 240px; object-fit: cover; border-radius: 8px;" />')
        return "No image"
    preview_image.short_description = "Preview"



@admin.register(Video)
class VideoAdmin(ModelAdmin):
    list_display = ('title', 'category', 'published_date')
    list_display_links = ('title',)
    list_filter = ('category', 'published_date')
    search_fields = ('title',)


@admin.register(GatedDownloadLead)
class GatedDownloadLeadAdmin(ModelAdmin):
    list_display = ('user_name', 'user_email', 'resource_title', 'downloaded_at')
    list_display_links = ('user_name',)
    search_fields = ('user_name', 'user_email', 'resource_title')
    list_filter = ('downloaded_at',)
    readonly_fields = ('downloaded_at',)


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'designation', 'category', 'linkedin_url', 'created_at', 'order_index')
    list_display_links = ('name', 'thumbnail_preview')
    search_fields = ('name', 'designation', 'bio', 'linkedin_url')
    list_filter = ('category', 'created_at')
    list_editable = ('order_index',)

    def thumbnail_preview(self, obj):
        img = obj.display_image
        if img:
            return mark_safe(f'<img src="{img}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />')
        return "-"
    thumbnail_preview.short_description = "Avatar"


@admin.register(Collaboration)
class CollaborationAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'category', 'support_level', 'created_at', 'website_url', 'order_index')
    list_display_links = ('name', 'thumbnail_preview')
    search_fields = ('name', 'blurb')
    list_filter = ('category', 'support_level', 'created_at')
    list_editable = ('order_index',)

    def thumbnail_preview(self, obj):
        logo = obj.display_logo
        if logo:
            return mark_safe(f'<img src="{logo}" style="width: 55px; height: 38px; border-radius: 6px; object-fit: cover;" />')
        return "-"
    thumbnail_preview.short_description = "Logo"


@admin.register(NewsFlash)
class NewsFlashAdmin(ModelAdmin):
    list_display = ('text', 'active', 'order_index', 'created_at')
    list_display_links = ('text',)
    list_editable = ('active', 'order_index')
    list_filter = ('active', 'created_at')
    search_fields = ('text', 'link_url')
    readonly_fields = ('created_at',)


@admin.register(UniqueVisitor)
class UniqueVisitorAdmin(ModelAdmin):
    list_display = ('ip_address', 'session_key', 'first_visited', 'last_visited')
    list_display_links = ('ip_address',)
    search_fields = ('ip_address', 'session_key')
    list_filter = ('first_visited', 'last_visited')
    readonly_fields = ('ip_address', 'session_key', 'first_visited', 'last_visited')


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        ('Landing Page — Hero Photo & Content Section', {
            'fields': (
                'hero_image',
                'hero_image_url',
                'home_hero_image_preview',
                'home_hero_badge',
                'home_hero_title',
                'home_hero_subtitle',
                'home_about_badge',
                'home_about_title',
                'home_about_text_1',
                'home_about_text_2',
            ),
            'description': 'Configure the public Landing Page (Homepage) hero background photo, headlines, and homepage overview section.'
        }),
        ('About Page — Hero Banner (The Fully Blue Section) & Showcase Image', {
            'fields': (
                'about_hero_badge',
                'about_hero_title',
                'about_hero_description',
                'about_image',
                'about_image_url',
                'about_image_caption',
                'about_hero_image_preview',
                'about_video_url',
            ),
            'description': 'Configure the top blue hero banner of the About page. The showcase image has its own dedicated card within the blue section.'
        }),
        ('About Page — Profile Section', {
            'fields': (
                'profile_badge',
                'profile_title',
                'profile_text',
                'profile_feature_1_title',
                'profile_feature_1_text',
                'profile_feature_2_title',
                'profile_feature_2_text',
            ),
            'description': 'Edit the coalition profile story and the two core highlight pillars.'
        }),
        ('About Page — Strategic Mission & Vision', {
            'fields': (
                'vision_title',
                'vision_text',
                'mission_title',
                'mission_text',
            ),
            'description': 'Edit the strategic vision and mission statements.'
        }),
        ('Support Us — Bank & Financial Details', {
            'fields': (
                'bank_name',
                'bank_account_name',
                'bank_account_no',
                'bank_branch',
                'bank_qr_image',
            ),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('home_hero_image_preview', 'about_hero_image_preview')

    def home_hero_image_preview(self, obj):
        img = obj.display_hero_image
        if img:
            return mark_safe(f'<img src="{img}" style="max-width: 320px; max-height: 200px; object-fit: cover; border-radius: 10px; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />')
        return mark_safe('<span style="color: #94a3b8;">No hero background image set (using default navy theme gradient).</span>')
    home_hero_image_preview.short_description = "Landing Hero Image Preview"

    def about_hero_image_preview(self, obj):
        img = obj.display_about_image
        if img:
            return mark_safe(f'<img src="{img}" style="max-width: 320px; max-height: 220px; object-fit: cover; border-radius: 10px; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />')
        return mark_safe('<span style="color: #94a3b8;">No showcase image set. Default advocacy image will be displayed.</span>')
    about_hero_image_preview.short_description = "About Showcase Image Preview"

    def has_add_permission(self, request):
        return False if SiteSettings.objects.exists() else True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ThematicSector)
class ThematicSectorAdmin(ModelAdmin):
    list_display = ('title', 'icon_preview', 'order_index')
    list_editable = ('order_index',)
    search_fields = ('title', 'description')

    def icon_preview(self, obj):
        return mark_safe(f'<i class="{escape(obj.icon)}" style="font-size: 18px; color: #2085AB;"></i> <span style="font-size: 11px; color: #64748b; margin-left: 6px;">{escape(obj.icon)}</span>')
    icon_preview.short_description = "Icon"
