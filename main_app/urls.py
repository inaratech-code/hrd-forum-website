from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('api/stats', views.api_stats, name='api_stats'),
    path('api/provinces', views.api_provinces, name='api_provinces'),
    path('api/province/<int:prov_id>', views.api_province_detail, name='api_province_detail'),
    path('api/news', views.api_news, name='api_news'),
    path('api/resources', views.api_resources, name='api_resources'),
    path('api/popup', views.api_popup, name='api_popup'),
    path('api/gallery', views.api_gallery, name='api_gallery'),
    path('api/blogs', views.api_blogs, name='api_blogs'),
    path('api/videos', views.api_videos, name='api_videos'),
    path('api/membership', views.submit_membership, name='submit_membership'),
    path('api/incident', views.submit_incident, name='submit_incident'),
    path('api/resource/download-access', views.request_gated_download, name='request_gated_download'),
]
