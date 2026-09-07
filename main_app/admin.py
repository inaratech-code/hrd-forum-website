from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.utils.html import mark_safe, escape

from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Video, GatedDownloadLead,
    TeamMember, Collaboration, NewsFlash, UniqueVisitor
)


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
    list_display = ('title', 'category', 'format', 'file_size', 'is_gated')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('category', 'format', 'is_gated')
    inlines = [GatedDownloadLeadInline]


@admin.register(Membership)
class MembershipAdmin(ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'province', 'organization', 'role', 'status_badge', 'created_at')
    list_display_links = ('full_name',)
    search_fields = ('full_name', 'email', 'province__name', 'organization')
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

    def thumbnail_preview(self, obj):
        img = obj.display_image
        if img:
            return mark_safe(f'<img src="{img}" style="width: 55px; height: 38px; object-fit: cover; border-radius: 6px;" />')
        return "-"
    thumbnail_preview.short_description = "Thumbnail"


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
    list_display = ('thumbnail_preview', 'name', 'designation', 'category', 'created_at', 'order_index')
    list_display_links = ('name', 'thumbnail_preview')
    search_fields = ('name', 'designation', 'bio')
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
    list_display = ('thumbnail_preview', 'name', 'category', 'created_at', 'website_url', 'order_index')
    list_display_links = ('name', 'thumbnail_preview')
    search_fields = ('name', 'blurb')
    list_filter = ('category', 'created_at')
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