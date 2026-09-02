from django.contrib import admin
from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Blog, Video, GatedDownloadLead,
    TeamMember, Collaboration
)

@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    list_display = ('provincial_networks', 'monitored_defenders', 'resolved_cases', 'total_visitors')

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'base_city', 'coordinators_count', 'helpline_phone', 'active_cases')
    search_fields = ('name', 'base_city', 'address')
    list_filter = ('base_city',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_str')
    search_fields = ('title', 'summary')
    list_filter = ('category',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'format', 'file_size', 'is_gated')
    search_fields = ('title',)
    list_filter = ('category', 'format', 'is_gated')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'province', 'organization', 'role', 'status', 'created_at')
    search_fields = ('full_name', 'email', 'province', 'organization')
    list_filter = ('status', 'province', 'created_at')
    list_editable = ('status',)

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('reporter_name', 'province', 'incident_type', 'priority', 'contact_info', 'created_at')
    search_fields = ('reporter_name', 'contact_info', 'province', 'details')
    list_filter = ('province', 'incident_type', 'priority')

@admin.register(PopupConfig)
class PopupConfigAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'link_text', 'link_url')
    list_editable = ('active',)

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_str')
    search_fields = ('title', 'author', 'content')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_str')

@admin.register(GatedDownloadLead)
class GatedDownloadLeadAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'resource_title', 'downloaded_at')
    search_fields = ('user_name', 'user_email', 'resource_title')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'category', 'order_index')
    search_fields = ('name', 'designation', 'bio')
    list_filter = ('category',)
    list_editable = ('order_index',)

@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'website_url', 'order_index')
    search_fields = ('name', 'blurb')
    list_filter = ('category',)
    list_editable = ('order_index',)
