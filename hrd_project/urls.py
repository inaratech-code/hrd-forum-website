from pathlib import Path

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.views.static import serve as static_serve


def serve_media(request, path):
    """Serve local media files; if missing, redirect to R2 when configured."""
    local_file = Path(settings.MEDIA_ROOT) / path
    if local_file.is_file():
        return static_serve(request, path, document_root=settings.MEDIA_ROOT)

    if getattr(settings, 'USE_R2_STORAGE', False):
        import boto3
        from botocore.client import Config

        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto',
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': path},
            ExpiresIn=3600,
        )
        return HttpResponseRedirect(url)

    raise Http404(f'media file not found: {path}')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    re_path(r'^media/(?P<path>.*)$', serve_media),
]

handler404 = 'main_app.views.custom_404_view'
handler500 = 'main_app.views.custom_500_view'
