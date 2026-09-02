from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('api/stats', views.api_stats, name='api_stats'),
    path('api/provinces', views.api_provinces, name='api_provinces'),
    path('api/province/<int:prov_id>', views.api_province_detail, name='api_province_detail'),
    path('api/news', views.api_news, name='api_news'),
    path('api/news/<int:news_id>', views.api_news_detail, name='api_news_detail'),
    path('api/resources', views.api_resources, name='api_resources'),
    path('api/popup', views.api_popup, name='api_popup'),
    path('api/gallery', views.api_gallery, name='api_gallery'),
    path('api/blogs', views.api_blogs, name='api_blogs'),
    path('api/videos', views.api_videos, name='api_videos'),
    path('api/news-flashes', views.api_news_flashes, name='api_news_flashes'),
    path('api/membership', views.submit_membership, name='submit_membership'),
    path('api/incident', views.submit_incident, name='submit_incident'),
    path('api/resource/download-access', views.request_gated_download, name='request_gated_download'),

    # Admin Portal Routes
    path('api/admin/login', views.admin_login, name='admin_login'),
    path('api/admin/logout', views.admin_logout, name='admin_logout'),
    path('api/admin/news', views.admin_news_manage, name='admin_news_manage'),
    path('api/admin/news/<int:news_id>', views.admin_news_manage, name='admin_news_delete'),
    path('api/admin/popup', views.admin_popup_manage, name='admin_popup_manage'),
    path('api/admin/gallery', views.admin_gallery_manage, name='admin_gallery_manage'),
    path('api/admin/gallery/<int:photo_id>', views.admin_gallery_manage, name='admin_gallery_delete'),
    path('api/admin/resources', views.admin_resources_manage, name='admin_resources_manage'),
    path('api/admin/resources/<int:res_id>', views.admin_resources_manage, name='admin_resources_delete'),
    path('api/admin/gated-logs', views.admin_gated_logs, name='admin_gated_logs'),
    path('api/incidents', views.admin_incidents_list, name='admin_incidents_list'),
    path('api/memberships', views.admin_memberships_list, name='admin_memberships_list'),

    # Team & Collaboration Routes
    path('api/team', views.api_team, name='api_team'),
    path('api/collaborations', views.api_collaborations, name='api_collaborations'),
    path('api/admin/team', views.admin_team_manage, name='admin_team_manage'),
    path('api/admin/team/<int:member_id>', views.admin_team_manage, name='admin_team_delete'),
    path('api/admin/collaborations', views.admin_collaborations_manage, name='admin_collaborations_manage'),
    path('api/admin/collaborations/<int:collab_id>', views.admin_collaborations_manage, name='admin_collaborations_delete'),
]
