from django.urls import path
from . import views
from . import portal_views

urlpatterns = [
    # Frontend Entry
    path('', views.index_page, name='index'),
    path('public/', views.index_page, name='index_public'),

    # Standalone Custom Portal Routes (/portal/)
    path('portal/login/', portal_views.portal_login_view, name='portal_login'),
    path('portal/logout/', portal_views.portal_logout_view, name='portal_logout'),
    path('portal/', portal_views.portal_dashboard_view, name='portal_dashboard'),

    # Portal Photo Gallery CRUD
    path('portal/gallery/', portal_views.portal_gallery_list, name='portal_gallery_list'),
    path('portal/gallery/add/', portal_views.portal_gallery_add, name='portal_gallery_add'),
    path('portal/gallery/<int:photo_id>/edit/', portal_views.portal_gallery_edit, name='portal_gallery_edit'),
    path('portal/gallery/<int:photo_id>/delete/', portal_views.portal_gallery_delete, name='portal_gallery_delete'),

    # Portal Resources CRUD
    path('portal/resources/', portal_views.portal_resource_list, name='portal_resource_list'),
    path('portal/resources/add/', portal_views.portal_resource_add, name='portal_resource_add'),
    path('portal/resources/<int:res_id>/edit/', portal_views.portal_resource_edit, name='portal_resource_edit'),
    path('portal/resources/<int:res_id>/delete/', portal_views.portal_resource_delete, name='portal_resource_delete'),

    # Portal Incidents & Memberships
    path('portal/incidents/', portal_views.portal_incidents_list, name='portal_incidents_list'),
    path('portal/memberships/', portal_views.portal_memberships_list, name='portal_memberships_list'),

    # Public Read API Endpoints
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/provinces/', views.api_provinces, name='api_provinces'),
    path('api/provinces/<int:prov_id>/', views.api_province_detail, name='api_province_detail'),
    path('api/news/', views.api_news, name='api_news'),
    path('api/news/<int:news_id>/', views.api_news_detail, name='api_news_detail'),
    path('api/resources/', views.api_resources, name='api_resources'),
    path('api/popup/', views.api_popup, name='api_popup'),
    path('api/gallery/', views.api_gallery, name='api_gallery'),
    path('api/blogs/', views.api_blogs, name='api_blogs'),
    path('api/videos/', views.api_videos, name='api_videos'),
    path('api/news-flashes/', views.api_news_flashes, name='api_news_flashes'),
    path('api/team/', views.api_team, name='api_team'),
    path('api/collaborations/', views.api_collaborations, name='api_collaborations'),

    # Public Submissions / Actions
    path('api/membership/', views.submit_membership, name='submit_membership'),
    path('api/incident/', views.submit_incident, name='submit_incident'),
    path('api/resource/download-access/', views.request_gated_download, name='request_gated_download'),

    # Legacy Admin API
    path('api/admin/login/', views.admin_login, name='admin_login'),
    path('api/admin/logout/', views.admin_logout, name='admin_logout'),
    path('api/admin/news/', views.admin_news_manage, name='admin_news_manage'),
    path('api/admin/popup/', views.admin_popup_manage, name='admin_popup_manage'),
    path('api/admin/gallery/', views.admin_gallery_manage, name='admin_gallery_manage'),
    path('api/admin/resources/', views.admin_resources_manage, name='admin_resources_manage'),
    path('api/admin/incidents/', views.admin_incidents_list, name='admin_incidents_list'),
    path('api/admin/memberships/', views.admin_memberships_list, name='admin_memberships_list'),
]