import os
import json
import uuid
import logging
from pathlib import Path
from functools import wraps

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.db.models import F

from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Blog, Video, GatedDownloadLead,
    TeamMember, Collaboration, NewsFlash, UniqueVisitor
)

logger = logging.getLogger(__name__)

# UTILITY HELPERS

def admin_dashboard_context(request):
    if request.path.startswith('/admin/'):
        try:
            incidents_total = Incident.objects.count()
            incidents_urgent = Incident.objects.filter(priority__in=['Urgent', 'High']).count()
            memberships_pending = Membership.objects.filter(status='pending').count()
            memberships_total = Membership.objects.count()
            news_total = News.objects.count()
            provinces_total = Province.objects.count()

            # Priority counts
            inc_urgent = Incident.objects.filter(priority='Urgent').count()
            inc_high = Incident.objects.filter(priority='High').count()
            inc_medium = Incident.objects.filter(priority='Medium').count()
            inc_low = Incident.objects.filter(priority='Low').count()

            recent_incidents = list(Incident.objects.order_by('-created_at')[:5])
            recent_memberships = list(Membership.objects.order_by('-created_at')[:5])

            stats_obj = Stats.objects.first()
            visitors_total = stats_obj.total_visitors if stats_obj else UniqueVisitor.objects.count()

            return {
                'kpi_incidents_total': incidents_total,
                'kpi_incidents_urgent': incidents_urgent,
                'kpi_memberships_pending': memberships_pending,
                'kpi_memberships_total': memberships_total,
                'kpi_news_total': news_total,
                'kpi_provinces_total': provinces_total,
                'kpi_visitors_total': visitors_total,
                'inc_urgent_count': inc_urgent,
                'inc_high_count': inc_high,
                'inc_medium_count': inc_medium,
                'inc_low_count': inc_low,
                'recent_incidents_list': recent_incidents,
                'recent_memberships_list': recent_memberships,
            }
        except Exception as e:
            logger.error(f"Error building admin context: {e}")
    return {}

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def _track_visitor(request):
    try:
        if not request.session.session_key:
            request.session.save()

        ip = _get_client_ip(request)
        session_key = request.session.session_key or ''
        has_visited = request.session.get('has_visited_hrd', False)

        if not has_visited:
            visitor, created = UniqueVisitor.objects.get_or_create(
                ip_address=ip,
                defaults={'session_key': session_key}
            )
            request.session['has_visited_hrd'] = True

            if created:
                stats = Stats.objects.first()
                if not stats:
                    Stats.objects.create(total_visitors=1)
                else:
                    Stats.objects.filter(pk=stats.pk).update(total_visitors=F('total_visitors') + 1)
            else:
                visitor.save(update_fields=['last_visited'])
    except Exception as e:
        logger.warning(f"Visitor tracking failed: {e}")

def parse_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return {}
    return request.POST.dict()

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        admin_token = getattr(settings, 'ADMIN_API_TOKEN', os.environ.get('ADMIN_API_TOKEN', 'hrd_session_admin_secure_token_2026'))
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        is_token_auth = (admin_token and admin_token in auth_header)
        if not (is_token_auth or (request.user and request.user.is_authenticated and request.user.is_staff)):
            return JsonResponse({"success": False, "error": "Unauthorized access. Staff credentials required."}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# PUBLIC READ ENDPOINTS

def index_page(request):
    _track_visitor(request)
    return render(request, 'index.html')

def api_stats(request):
    _track_visitor(request)
    stats = Stats.objects.first()
    if not stats:
        stats = Stats.objects.create(total_visitors=0)

    return JsonResponse({
        "provincial_networks": stats.provincial_networks,
        "monitored_defenders": str(stats.monitored_defenders),
        "resolved_cases": str(stats.resolved_cases),
        "total_visitors": stats.total_visitors,
    })

def api_provinces(request):
    provinces = Province.objects.all().order_by('id')
    data = [{
        "id": p.id,
        "name": p.name,
        "code": p.code,
        "base_city": p.base_city,
        "coords_lat": p.coords_lat,
        "coords_lng": p.coords_lng,
        "coordinators_count": p.coordinators_count,
        "districts_count": p.districts_count,
        "helpline_phone": p.helpline_phone,
        "address": p.address,
        "active_cases": p.active_cases,
        "description": p.description,
        "long_summary": p.long_summary
    } for p in provinces]
    return JsonResponse(data, safe=False)

def api_province_detail(request, prov_id):
    try:
        p = Province.objects.get(pk=prov_id)
        return JsonResponse({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "base_city": p.base_city,
            "coords_lat": p.coords_lat,
            "coords_lng": p.coords_lng,
            "coordinators_count": p.coordinators_count,
            "districts_count": p.districts_count,
            "helpline_phone": p.helpline_phone,
            "address": p.address,
            "active_cases": p.active_cases,
            "description": p.description,
            "long_summary": p.long_summary
        })
    except Province.DoesNotExist:
        return JsonResponse({"error": "Province not found"}, status=404)

def api_news(request):
    news_items = News.objects.all().order_by('-published_date')
    data = [{
        "id": n.id,
        "title": n.title,
        "date_str": str(n.published_date),
        "image_url": n.display_image,
        "category": n.category,
        "summary": n.summary,
        "content": n.content or n.summary or ''
    } for n in news_items]
    return JsonResponse(data, safe=False)

def api_news_detail(request, news_id):
    try:
        n = News.objects.get(pk=news_id)
        return JsonResponse({
            "id": n.id,
            "title": n.title,
            "date_str": str(n.published_date),
            "image_url": n.display_image,
            "category": n.category,
            "summary": n.summary,
            "content": n.content or n.summary or ''
        })
    except News.DoesNotExist:
        return JsonResponse({"error": "News article not found"}, status=404)

def api_resources(request):
    resources = Resource.objects.all().order_by('id')
    data = [{
        "id": r.id,
        "title": r.title,
        "category": r.category,
        "format": r.format,
        "file_size": r.file_size,
        "file_url": r.display_file,
        "is_gated": r.is_gated
    } for r in resources]
    return JsonResponse(data, safe=False)

def api_popup(request):
    popup = PopupConfig.objects.filter(active=True).first()
    if popup:
        return JsonResponse({
            "id": popup.id,
            "image_url": popup.display_image,
            "title": popup.title,
            "subtitle": popup.subtitle,
            "link_url": popup.link_url,
            "link_text": popup.link_text,
            "active": 1 if popup.active else 0
        })
    return JsonResponse({"active": 0})

def api_gallery(request):
    photos = Gallery.objects.all().order_by('-id')
    data = [{
        "id": g.id,
        "title": g.title,
        "image_url": g.display_image,
        "category": g.category
    } for g in photos]
    return JsonResponse(data, safe=False)

def api_blogs(request):
    blogs = Blog.objects.all().order_by('-published_date')
    data = [{
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "date_str": str(b.published_date),
        "content": b.content,
        "image_url": b.display_image
    } for b in blogs]
    return JsonResponse(data, safe=False)

def api_videos(request):
    videos = Video.objects.all().order_by('-published_date')
    data = [{
        "id": v.id,
        "title": v.title,
        "embed_url": v.embed_url,
        "category": v.category,
        "date_str": str(v.published_date)
    } for v in videos]
    return JsonResponse(data, safe=False)

def api_news_flashes(request):
    flashes = NewsFlash.objects.filter(active=True).order_by('order_index', '-created_at')
    data = [{
        "id": f.id,
        "text": f.text,
        "link_url": f.link_url or ''
    } for f in flashes]
    return JsonResponse(data, safe=False)

def api_team(request):
    category = request.GET.get('category')
    queryset = TeamMember.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    data = [{
        "id": item.id,
        "name": item.name,
        "designation": item.designation,
        "category": item.category,
        "bio": item.bio,
        "image_url": item.display_image,
        "order_index": item.order_index
    } for item in queryset]
    return JsonResponse(data, safe=False)

def api_collaborations(request):
    category = request.GET.get('category')
    queryset = Collaboration.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    data = [{
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "logo_url": item.display_logo,
        "blurb": item.blurb,
        "website_url": item.website_url,
        "order_index": item.order_index
    } for item in queryset]
    return JsonResponse(data, safe=False)

# PUBLIC SUBMISSIONS

@csrf_exempt
def request_gated_download(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = parse_request_data(request)
    user_name = (data.get('user_name') or '').strip()
    user_email = (data.get('user_email') or '').strip()
    resource_id = data.get('resource_id')

    if not user_name or not user_email or not resource_id:
        return JsonResponse({"success": False, "error": "Name, Email, and Resource ID required."}, status=400)

    try:
        res_obj = Resource.objects.get(pk=resource_id)
    except Resource.DoesNotExist:
        return JsonResponse({"success": False, "error": "Resource not found."}, status=404)

    GatedDownloadLead.objects.create(
        user_name=user_name,
        user_email=user_email,
        resource=res_obj,
        resource_title=res_obj.title
    )

    return JsonResponse({
        "success": True,
        "download_url": res_obj.display_file,
        "message": f"Thank you, {user_name}. Your download has been authorized!"
    })

@csrf_exempt
def submit_membership(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = parse_request_data(request)
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    province_raw = (data.get('province') or '').strip()
    organization = (data.get('organization') or '').strip()
    role = (data.get('role') or '').strip()

    if not full_name or not email or not province_raw:
        return JsonResponse({"success": False, "error": "Full Name, Email, and Province are required."}, status=400)

    province_clean = province_raw.replace('Province', '').strip()
    prov_obj = (
        Province.objects.filter(name__icontains=province_clean).first() or
        Province.objects.filter(code__iexact=province_raw.strip()).first() or
        (Province.objects.filter(pk=int(province_raw)).first() if province_raw.isdigit() else None)
    )
    if not prov_obj:
        return JsonResponse({"success": False, "error": f"Invalid province: {province_raw}"}, status=400)

    m = Membership.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        province=prov_obj,
        organization=organization,
        role=role
    )

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hrdforum.org')
        admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', 'alerts@hrdforum.org')

        admin_subject = f"[NEW MEMBERSHIP] {m.full_name} - {prov_obj.name}"
        admin_body = (
            f"NEW MEMBERSHIP APPLICATION (#{m.id})\n"
            f"Name: {m.full_name}\nEmail: {m.email}\nPhone: {m.phone or 'N/A'}\n"
            f"Province: {prov_obj.name}\nOrganization: {m.organization or 'N/A'}\n"
            f"Submitted At: {m.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_mail(admin_subject, admin_body, from_email, [admin_email], fail_silently=True)

        applicant_subject = "HRD Forum Nepal Membership Application Confirmation"
        applicant_body = (
            f"Dear {m.full_name},\n\n"
            f"Thank you for applying to the HRD Forum Nepal network in {prov_obj.name}.\n"
            f"Your application (Ref #{m.id}) is under review.\n\n"
            f"Regards,\nHRD Forum Nepal"
        )
        send_mail(applicant_subject, applicant_body, from_email, [m.email], fail_silently=True)
    except Exception as err:
        logger.error(f"Membership email error for ID #{m.id}: {err}")

    return JsonResponse({
        "success": True,
        "id": m.id,
        "message": "Membership application submitted successfully!"
    }, status=201)

@csrf_exempt
def submit_incident(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = parse_request_data(request)
    reporter_name = (data.get('reporter_name') or '').strip()
    contact_info = (data.get('contact_info') or '').strip()
    province_raw = (data.get('province') or '').strip()
    incident_type = (data.get('incident_type') or 'Urgent Support').strip()
    details = (data.get('details') or '').strip()
    priority = (data.get('priority') or 'High').strip()

    if not reporter_name or not contact_info or not province_raw or not details:
        return JsonResponse({"success": False, "error": "Reporter Name, Contact Info, Province, and Details required."}, status=400)

    province_clean = province_raw.replace('Province', '').strip()
    prov_obj = (
        Province.objects.filter(name__icontains=province_clean).first() or
        Province.objects.filter(code__iexact=province_raw.strip()).first() or
        (Province.objects.filter(pk=int(province_raw)).first() if province_raw.isdigit() else None)
    )
    if not prov_obj:
        return JsonResponse({"success": False, "error": f"Invalid province: {province_raw}"}, status=400)

    inc = Incident.objects.create(
        reporter_name=reporter_name,
        contact_info=contact_info,
        province=prov_obj,
        incident_type=incident_type,
        details=details,
        priority=priority
    )

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hrdforum.org')
        admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', 'alerts@hrdforum.org')

        recipients = [admin_email]
        if prov_obj.helpdesk_email and prov_obj.helpdesk_email not in recipients:
            recipients.append(prov_obj.helpdesk_email)

        subject = f"[URGENT ALERT] {inc.incident_type} - {prov_obj.name} (#{inc.id})"
        body = (
            f"URGENT INCIDENT REPORT (#{inc.id})\n"
            f"Reporter: {inc.reporter_name}\nContact: {inc.contact_info}\n"
            f"Province: {prov_obj.name}\nPriority: {inc.priority}\n"
            f"Details:\n{inc.details}"
        )
        send_mail(subject, body, from_email, recipients, fail_silently=True)
    except Exception as err:
        logger.error(f"Incident email error #{inc.id}: {err}")

    return JsonResponse({
        "success": True,
        "id": inc.id,
        "message": "Incident report logged securely."
    }, status=201)

# AUTHENTICATION

@csrf_exempt
def admin_login(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    data = parse_request_data(request)
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    user = authenticate(request, username=username, password=password)
    if user and user.is_staff:
        login(request, user)
        token = getattr(settings, 'ADMIN_API_TOKEN', os.environ.get('ADMIN_API_TOKEN', 'hrd_session_admin_secure_token_2026'))
        return JsonResponse({
            "success": True,
            "token": token,
            "username": username,
            "message": "Admin authorization successful!"
        })

    return JsonResponse({"success": False, "error": "Invalid credentials or non-staff access."}, status=401)

@csrf_exempt
def admin_logout(request):
    logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully."})

# PROTECTED ADMIN ENDPOINTS

@csrf_exempt
@staff_required
def admin_news_manage(request, news_id=None):
    if request.method == 'POST':
        data = parse_request_data(request)
        if news_id:
            try:
                n = News.objects.get(pk=news_id)
                n.title = data.get('title', n.title)
                n.summary = data.get('summary', n.summary)
                n.content = data.get('content', n.content)
                n.category = data.get('category', n.category)
                n.image_url = data.get('image_url', n.image_url)
                n.save()
                return JsonResponse({"success": True, "id": n.id, "message": "News item updated."})
            except News.DoesNotExist:
                return JsonResponse({"error": "News not found"}, status=404)
        else:
            n = News.objects.create(
                title=data.get('title', 'News Update'),
                category=data.get('category', 'General'),
                summary=data.get('summary', ''),
                content=data.get('content', ''),
                image_url=data.get('image_url', '')
            )
            return JsonResponse({"success": True, "id": n.id, "message": "News item published."})

    elif request.method == 'DELETE' and news_id:
        News.objects.filter(id=news_id).delete()
        return JsonResponse({"success": True, "message": "News item deleted."})

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_popup_manage(request):
    if request.method == 'POST':
        data = parse_request_data(request)
        popup = PopupConfig.objects.first() or PopupConfig()
        popup.image_url = data.get('image_url', popup.image_url)
        popup.title = data.get('title', popup.title)
        popup.subtitle = data.get('subtitle', popup.subtitle)
        popup.link_url = data.get('link_url', popup.link_url)
        popup.link_text = data.get('link_text', popup.link_text)
        act_val = data.get('active', 1)
        popup.active = bool(act_val) if not isinstance(act_val, str) else act_val.lower() in ('true', '1', 't')
        popup.save()
        return JsonResponse({"success": True, "message": "Popup configuration updated!"})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_gallery_manage(request, photo_id=None):
    if request.method == 'POST':
        data = parse_request_data(request)
        g = Gallery.objects.create(
            title=data.get('title', 'Gallery Photo'),
            image_url=data.get('image_url', ''),
            category=data.get('category', 'General')
        )
        return JsonResponse({"success": True, "id": g.id, "message": "Photo saved."})
    elif request.method == 'DELETE' and photo_id:
        Gallery.objects.filter(id=photo_id).delete()
        return JsonResponse({"success": True, "message": "Photo deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_video_manage(request, video_id=None):
    if request.method == 'POST':
        data = parse_request_data(request)
        v = Video.objects.create(
            title=data.get('title', 'Video Documentary'),
            embed_url=data.get('embed_url', ''),
            category=data.get('category', 'Documentary')
        )
        return JsonResponse({"success": True, "id": v.id, "message": "Video published."})
    elif request.method == 'DELETE' and video_id:
        Video.objects.filter(id=video_id).delete()
        return JsonResponse({"success": True, "message": "Video deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_resources_manage(request, res_id=None):
    if request.method == 'POST':
        data = parse_request_data(request)
        r = Resource.objects.create(
            title=data.get('title', 'Resource Document'),
            category=data.get('category', 'Document'),
            format=data.get('format', 'PDF'),
            file_size=data.get('file_size', '2.0 MB'),
            file_url=data.get('file_url', ''),
            is_gated=bool(data.get('is_gated', True))
        )
        return JsonResponse({"success": True, "id": r.id, "message": "Resource saved."})
    elif request.method == 'DELETE' and res_id:
        Resource.objects.filter(id=res_id).delete()
        return JsonResponse({"success": True, "message": "Resource deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_team_manage(request, member_id=None):
    if request.method == 'POST':
        data = parse_request_data(request)
        t = TeamMember.objects.create(
            name=data.get('name', 'Team Member'),
            designation=data.get('designation', 'Coordinator'),
            category=data.get('category', 'executive'),
            bio=data.get('bio', ''),
            image_url=data.get('image_url', ''),
            order_index=int(data.get('order_index', 0))
        )
        return JsonResponse({"success": True, "id": t.id, "message": "Team member saved."})
    elif request.method == 'DELETE' and member_id:
        TeamMember.objects.filter(id=member_id).delete()
        return JsonResponse({"success": True, "message": "Team member deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_collaborations_manage(request, collab_id=None):
    if request.method == 'POST':
        data = parse_request_data(request)
        c = Collaboration.objects.create(
            name=data.get('name', 'Partner Organization'),
            category=data.get('category', 'institutional'),
            logo_url=data.get('logo_url', ''),
            blurb=data.get('blurb', ''),
            website_url=data.get('website_url', ''),
            order_index=int(data.get('order_index', 0))
        )
        return JsonResponse({"success": True, "id": c.id, "message": "Collaboration saved."})
    elif request.method == 'DELETE' and collab_id:
        Collaboration.objects.filter(id=collab_id).delete()
        return JsonResponse({"success": True, "message": "Collaboration deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_gated_logs(request):
    leads = GatedDownloadLead.objects.all().order_by('-downloaded_at')
    res = [{
        "id": l.id,
        "user_name": l.user_name,
        "user_email": l.user_email,
        "resource_title": l.resource_title or "Document",
        "downloaded_at": l.downloaded_at.strftime('%Y-%m-%d %H:%M') if l.downloaded_at else ""
    } for l in leads]
    return JsonResponse(res, safe=False)

@csrf_exempt
@staff_required
def admin_incidents_list(request):
    incidents = Incident.objects.select_related('province').all().order_by('-created_at')
    res = [{
        "id": i.id,
        "reporter_name": i.reporter_name,
        "contact_info": i.contact_info,
        "province": i.province.name if hasattr(i.province, 'name') else str(i.province),
        "incident_type": i.incident_type,
        "details": i.details,
        "priority": i.priority,
        "created_at": i.created_at.strftime('%Y-%m-%d %H:%M')
    } for i in incidents]
    return JsonResponse(res, safe=False)

@csrf_exempt
@staff_required
def admin_memberships_list(request):
    members = Membership.objects.select_related('province').all().order_by('-created_at')
    res = [{
        "id": m.id,
        "full_name": m.full_name,
        "email": m.email,
        "phone": m.phone,
        "province": m.province.name if hasattr(m.province, 'name') else str(m.province),
        "organization": m.organization,
        "role": m.role,
        "status": m.status,
        "created_at": m.created_at.strftime('%Y-%m-%d %H:%M')
    } for m in members]
    return JsonResponse(res, safe=False)

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.webp', '.doc', '.docx', '.txt'}

@csrf_exempt
@staff_required
def admin_upload_file(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)

    uploaded_file = request.FILES.get('file') or request.FILES.get('image') or request.FILES.get('document')
    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({"error": f"File type {ext} not allowed"}, status=400)

    upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
    os.makedirs(upload_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex[:10]}{ext}"
    file_path = upload_dir / unique_filename

    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    size_mb = uploaded_file.size / (1024 * 1024)
    file_size_str = f"{size_mb:.1f} MB" if size_mb >= 1.0 else f"{max(1, int(uploaded_file.size / 1024))} KB"

    raw_ext = ext.lstrip('.').upper() or 'FILE'
    format_display = 'PDF' if raw_ext == 'PDF' else ('IMAGE' if raw_ext in ('JPG', 'JPEG', 'PNG', 'WEBP') else 'DOCUMENT')
    rel_url = f"{settings.MEDIA_URL}uploads/{unique_filename}"

    return JsonResponse({
        "success": True,
        "url": rel_url,
        "filename": uploaded_file.name,
        "file_size": file_size_str,
        "format": format_display,
        "summary": f"{format_display} • {file_size_str}"
    })


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)