from django.urls import path
from . import views
from . import portal_views

urlpatterns = [
    # Frontend Entry
    path('', views.index_page, name='index'),
    path('public/', views.index_page, name='index_public'),
    path('support/', views.support_page_view, name='support_page'),
    path('about/', views.about_page, name='about_page'),
    path('gallery/', views.gallery_page, name='gallery_page'),
    path('news/<int:news_id>/', views.news_detail_page, name='news_detail'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # Custom Portal Authentication & Dashboard (/portal/)
    path('portal/login/', portal_views.portal_login_view, name='portal_login'),
    path('portal/logout/', portal_views.portal_logout_view, name='portal_logout'),
    path('portal/', portal_views.portal_dashboard_view, name='portal_dashboard'),
    path('portal/export/submissions.pdf', portal_views.portal_submission_pdf, name='portal_submission_pdf'),

    # Photo Gallery CRUD
    path('portal/gallery/', portal_views.portal_gallery_list, name='portal_gallery_list'),
    path('portal/gallery/add/', portal_views.portal_gallery_add, name='portal_gallery_add'),
    path('portal/gallery/<int:photo_id>/edit/', portal_views.portal_gallery_edit, name='portal_gallery_edit'),
    path('portal/gallery/<int:photo_id>/delete/', portal_views.portal_gallery_delete, name='portal_gallery_delete'),

    # Resources CRUD
    path('portal/resources/', portal_views.portal_resource_list, name='portal_resource_list'),
    path('portal/resources/add/', portal_views.portal_resource_add, name='portal_resource_add'),
    path('portal/resources/<int:res_id>/edit/', portal_views.portal_resource_edit, name='portal_resource_edit'),
    path('portal/resources/<int:res_id>/delete/', portal_views.portal_resource_delete, name='portal_resource_delete'),

    # Incidents CRUD
    path('portal/incidents/', portal_views.portal_incidents_list, name='portal_incidents_list'),
    path('portal/incidents/add/', portal_views.portal_incident_add, name='portal_incident_add'),
    path('portal/incidents/<int:incident_id>/edit/', portal_views.portal_incident_edit, name='portal_incident_edit'),
    path('portal/incidents/<int:incident_id>/delete/', portal_views.portal_incident_delete, name='portal_incident_delete'),

    # Memberships CRUD & Actions
    path('portal/memberships/', portal_views.portal_memberships_list, name='portal_memberships_list'),
    path('portal/memberships/add/', portal_views.portal_membership_add, name='portal_membership_add'),
    path('portal/memberships/<int:member_id>/edit/', portal_views.portal_membership_edit, name='portal_membership_edit'),
    path('portal/memberships/<int:member_id>/approve/', portal_views.portal_membership_approve, name='portal_membership_approve'),
    path('portal/memberships/<int:member_id>/reject/', portal_views.portal_membership_reject, name='portal_membership_reject'),
    path('portal/memberships/<int:member_id>/delete/', portal_views.portal_membership_delete, name='portal_membership_delete'),

    # News CRUD
    path('portal/news/', portal_views.portal_news_list, name='portal_news_list'),
    path('portal/news/add/', portal_views.portal_news_add, name='portal_news_add'),
    path('portal/news/<int:item_id>/edit/', portal_views.portal_news_edit, name='portal_news_edit'),
    path('portal/news/<int:item_id>/delete/', portal_views.portal_news_delete, name='portal_news_delete'),

    # Updates CRUD
    path('portal/updates/', portal_views.portal_updates_list, name='portal_updates_list'),
    path('portal/updates/add/', portal_views.portal_updates_add, name='portal_updates_add'),
    path('portal/updates/<int:item_id>/edit/', portal_views.portal_updates_edit, name='portal_updates_edit'),
    path('portal/updates/<int:item_id>/delete/', portal_views.portal_updates_delete, name='portal_updates_delete'),

    # Provinces CRUD
    path('portal/provinces/', portal_views.portal_province_list, name='portal_province_list'),
    path('portal/provinces/add/', portal_views.portal_province_add, name='portal_province_add'),
    path('portal/provinces/<int:prov_id>/edit/', portal_views.portal_province_edit, name='portal_province_edit'),
    path('portal/provinces/<int:prov_id>/delete/', portal_views.portal_province_delete, name='portal_province_delete'),

    # Team Members CRUD
    path('portal/team/', portal_views.portal_team_list, name='portal_team_list'),
    path('portal/team/add/', portal_views.portal_team_add, name='portal_team_add'),
    path('portal/team/<int:member_id>/edit/', portal_views.portal_team_edit, name='portal_team_edit'),
    path('portal/team/<int:member_id>/delete/', portal_views.portal_team_delete, name='portal_team_delete'),

    # Blogs CRUD
    path('portal/blogs/', portal_views.portal_blog_list, name='portal_blog_list'),
    path('portal/blogs/add/', portal_views.portal_blog_add, name='portal_blog_add'),
    path('portal/blogs/<int:blog_id>/edit/', portal_views.portal_blog_edit, name='portal_blog_edit'),
    path('portal/blogs/<int:blog_id>/delete/', portal_views.portal_blog_delete, name='portal_blog_delete'),

    # Videos CRUD
    path('portal/videos/', portal_views.portal_video_list, name='portal_video_list'),
    path('portal/videos/add/', portal_views.portal_video_add, name='portal_video_add'),
    path('portal/videos/<int:video_id>/edit/', portal_views.portal_video_edit, name='portal_video_edit'),
    path('portal/videos/<int:video_id>/delete/', portal_views.portal_video_delete, name='portal_video_delete'),

    # Collaborations CRUD
    path('portal/collaborations/', portal_views.portal_collaboration_list, name='portal_collaboration_list'),
    path('portal/collaborations/add/', portal_views.portal_collaboration_add, name='portal_collaboration_add'),
    path('portal/collaborations/<int:collab_id>/edit/', portal_views.portal_collaboration_edit, name='portal_collaboration_edit'),
    path('portal/collaborations/<int:collab_id>/delete/', portal_views.portal_collaboration_delete, name='portal_collaboration_delete'),

    # News Flashes CRUD
    path('portal/news-flashes/', portal_views.portal_news_flash_list, name='portal_news_flash_list'),
    path('portal/news-flashes/add/', portal_views.portal_news_flash_add, name='portal_news_flash_add'),
    path('portal/news-flashes/<int:flash_id>/edit/', portal_views.portal_news_flash_edit, name='portal_news_flash_edit'),
    path('portal/news-flashes/<int:flash_id>/delete/', portal_views.portal_news_flash_delete, name='portal_news_flash_delete'),

    # Popup Config CRUD
    path('portal/popups/', portal_views.portal_popup_list, name='portal_popup_list'),
    path('portal/popups/add/', portal_views.portal_popup_add, name='portal_popup_add'),
    path('portal/popups/<int:popup_id>/edit/', portal_views.portal_popup_edit, name='portal_popup_edit'),
    path('portal/popups/<int:popup_id>/delete/', portal_views.portal_popup_delete, name='portal_popup_delete'),

    # Gated Leads & Support
    path('portal/gated-leads/', portal_views.portal_gated_leads_list, name='portal_gated_leads_list'),
    path('portal/support-contributions/', portal_views.portal_contributions_list, name='portal_contributions_list'),

    # Users & Groups
    path('portal/users/', portal_views.portal_user_list, name='portal_user_list'),
    path('portal/users/add/', portal_views.portal_user_add, name='portal_user_add'),
    path('portal/users/<int:user_id>/edit/', portal_views.portal_user_edit, name='portal_user_edit'),
    path('portal/users/<int:user_id>/delete/', portal_views.portal_user_delete, name='portal_user_delete'),

    path('portal/groups/', portal_views.portal_group_list, name='portal_group_list'),
    path('portal/groups/add/', portal_views.portal_group_add, name='portal_group_add'),
    path('portal/groups/<int:group_id>/edit/', portal_views.portal_group_edit, name='portal_group_edit'),
    path('portal/groups/<int:group_id>/delete/', portal_views.portal_group_delete, name='portal_group_delete'),

    path('portal/settings/', portal_views.portal_settings_view, name='portal_settings'),
    path('portal/site-settings/', portal_views.portal_site_settings_view, name='portal_site_settings'),

    # Public Read API Endpoints (With and without trailing slashes)
    path('api/settings/', views.api_site_settings, name='api_site_settings'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/stats', views.api_stats),
    path('api/provinces/', views.api_provinces, name='api_provinces'),
    path('api/provinces', views.api_provinces),
    path('api/provinces/<int:prov_id>/', views.api_province_detail, name='api_province_detail'),
    path('api/provinces/<int:prov_id>', views.api_province_detail),
    path('api/province/<int:prov_id>/', views.api_province_detail),
    path('api/province/<int:prov_id>', views.api_province_detail),
    path('api/news/', views.api_news, name='api_news'),
    path('api/news', views.api_news),
    path('api/news/<int:news_id>/', views.api_news_detail, name='api_news_detail'),
    path('api/news/<int:news_id>', views.api_news_detail),
    path('api/updates/', views.api_updates, name='api_updates'),
    path('api/updates', views.api_updates),
    path('api/resources/', views.api_resources, name='api_resources'),
    path('api/resources', views.api_resources),
    path('api/popup/', views.api_popup, name='api_popup'),
    path('api/popup', views.api_popup),
    path('api/gallery/', views.api_gallery, name='api_gallery'),
    path('api/gallery', views.api_gallery),
    path('api/blogs/', views.api_blogs, name='api_blogs'),
    path('api/blogs', views.api_blogs),
    path('api/videos/', views.api_videos, name='api_videos'),
    path('api/videos', views.api_videos),
    path('api/news-flashes/', views.api_news_flashes, name='api_news_flashes'),
    path('api/news-flashes', views.api_news_flashes),
    path('api/team/', views.api_team, name='api_team'),
    path('api/team', views.api_team),
    path('api/collaborations/', views.api_collaborations, name='api_collaborations'),
    path('api/collaborations', views.api_collaborations),

    # Public Submissions / Actions
    path('api/membership/', views.submit_membership, name='submit_membership'),
    path('api/membership', views.submit_membership),
    path('api/incident/', views.submit_incident, name='submit_incident'),
    path('api/incident', views.submit_incident),
    path('api/resource/download-access/', views.request_gated_download, name='request_gated_download'),
    path('api/resource/download-access', views.request_gated_download),

    # Legacy admin JSON API — permanently retired (use /portal/)
    path('api/admin/login/', views.legacy_admin_api_disabled, name='admin_login'),
    path('api/admin/login', views.legacy_admin_api_disabled),
    path('api/admin/logout/', views.legacy_admin_api_disabled, name='admin_logout'),
    path('api/admin/logout', views.legacy_admin_api_disabled),
    path('api/admin/upload-file/', views.legacy_admin_api_disabled, name='admin_upload_file'),
    path('api/admin/upload-file', views.legacy_admin_api_disabled),

    path('api/admin/news/', views.legacy_admin_api_disabled, name='admin_news_manage'),
    path('api/admin/news', views.legacy_admin_api_disabled),
    path('api/admin/news/<int:news_id>/', views.legacy_admin_api_disabled, name='admin_news_manage_id'),
    path('api/admin/news/<int:news_id>', views.legacy_admin_api_disabled),

    path('api/admin/popup/', views.legacy_admin_api_disabled, name='admin_popup_manage'),
    path('api/admin/popup', views.legacy_admin_api_disabled),

    path('api/admin/gallery/', views.legacy_admin_api_disabled, name='admin_gallery_manage'),
    path('api/admin/gallery', views.legacy_admin_api_disabled),
    path('api/admin/gallery/<int:photo_id>/', views.legacy_admin_api_disabled, name='admin_gallery_manage_id'),
    path('api/admin/gallery/<int:photo_id>', views.legacy_admin_api_disabled),

    path('api/admin/resources/', views.legacy_admin_api_disabled, name='admin_resources_manage'),
    path('api/admin/resources', views.legacy_admin_api_disabled),
    path('api/admin/resources/<int:res_id>/', views.legacy_admin_api_disabled, name='admin_resources_manage_id'),
    path('api/admin/resources/<int:res_id>', views.legacy_admin_api_disabled),

    path('api/admin/videos/', views.legacy_admin_api_disabled, name='admin_video_manage'),
    path('api/admin/videos', views.legacy_admin_api_disabled),
    path('api/admin/videos/<int:video_id>/', views.legacy_admin_api_disabled, name='admin_video_manage_id'),
    path('api/admin/videos/<int:video_id>', views.legacy_admin_api_disabled),

    path('api/admin/team/', views.legacy_admin_api_disabled, name='admin_team_manage'),
    path('api/admin/team', views.legacy_admin_api_disabled),
    path('api/admin/team/<int:member_id>/', views.legacy_admin_api_disabled, name='admin_team_manage_id'),
    path('api/admin/team/<int:member_id>', views.legacy_admin_api_disabled),

    path('api/admin/collaborations/', views.legacy_admin_api_disabled, name='admin_collaborations_manage'),
    path('api/admin/collaborations', views.legacy_admin_api_disabled),
    path('api/admin/collaborations/<int:collab_id>/', views.legacy_admin_api_disabled, name='admin_collaborations_manage_id'),
    path('api/admin/collaborations/<int:collab_id>', views.legacy_admin_api_disabled),

    path('api/admin/gated-logs/', views.legacy_admin_api_disabled, name='admin_gated_logs'),
    path('api/admin/gated-logs', views.legacy_admin_api_disabled),

    path('api/incidents/', views.legacy_admin_api_disabled, name='api_incidents_list'),
    path('api/incidents', views.legacy_admin_api_disabled),
    path('api/admin/incidents/', views.legacy_admin_api_disabled, name='admin_incidents_list'),
    path('api/admin/incidents', views.legacy_admin_api_disabled),

    path('api/memberships/', views.legacy_admin_api_disabled, name='api_memberships_list'),
    path('api/memberships', views.legacy_admin_api_disabled),
    path('api/admin/memberships/', views.legacy_admin_api_disabled, name='admin_memberships_list'),
    path('api/admin/memberships', views.legacy_admin_api_disabled),
]
