from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Blog, Video, GatedDownloadLead,
    TeamMember, Collaboration, NewsFlash, UniqueVisitor
)

from django.db.models import F

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def _track_visitor(request):
    """
    Tracks unique website visitors using client IP address & session state.
    Increments total_visitors ONLY when a new unique visitor is detected.
    """
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
                Stats.objects.create(provincial_networks=7, monitored_defenders="1,200+", resolved_cases="150+", total_visitors=1)
            else:
                Stats.objects.filter(pk=stats.pk).update(total_visitors=F('total_visitors') + 1)
        else:
            visitor.save()

def index_page(request):
    _track_visitor(request)
    return render(request, 'index.html')

def api_stats(request):
    _track_visitor(request)
    stats = Stats.objects.first()
    if not stats:
        stats = Stats.objects.create(provincial_networks=7, monitored_defenders="1,200+", resolved_cases="150+", total_visitors=0)

    return JsonResponse({
        "provincial_networks": stats.provincial_networks,
        "monitored_defenders": stats.monitored_defenders,
        "resolved_cases": stats.resolved_cases,
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
            "helpline_phone": p.helpline_phone,
            "address": p.address,
            "active_cases": p.active_cases,
            "description": p.description,
            "long_summary": p.long_summary
        })
    except Province.DoesNotExist:
        return JsonResponse({"error": "Province not found"}, status=404)

def api_news(request):
    news_items = News.objects.all().order_by('-id')
    data = [{
        "id": n.id,
        "title": n.title,
        "date_str": n.date_str,
        "image_url": n.image_url,
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
            "date_str": n.date_str,
            "image_url": n.image_url,
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
        "file_url": r.file_url,
        "is_gated": r.is_gated
    } for r in resources]
    return JsonResponse(data, safe=False)

def api_popup(request):
    popup = PopupConfig.objects.filter(active=True).first()
    if popup:
        return JsonResponse({
            "id": popup.id,
            "image_url": popup.image_url,
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
        "image_url": g.image_url,
        "category": g.category
    } for g in photos]
    return JsonResponse(data, safe=False)

def api_blogs(request):
    blogs = Blog.objects.all().order_by('-id')
    data = [{
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "date_str": b.date_str,
        "content": b.content,
        "image_url": b.image_url
    } for b in blogs]
    return JsonResponse(data, safe=False)

def api_videos(request):
    videos = Video.objects.all().order_by('-id')
    data = [{
        "id": v.id,
        "title": v.title,
        "embed_url": v.embed_url,
        "category": v.category,
        "date_str": v.date_str
    } for v in videos]
    return JsonResponse(data, safe=False)

def api_news_flashes(request):
    flashes = NewsFlash.objects.filter(active=True).order_by('order_index', '-created_at')
    data = []
    for f in flashes:
        link = (f.link_url or '').strip()
        if not (link.startswith('http://') or link.startswith('https://')):
            link = ''
        data.append({
            "id": f.id,
            "text": f.text,
            "link_url": link
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def request_gated_download(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

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
        resource_id=resource_id,
        resource_title=res_obj.title
    )

    return JsonResponse({
        "success": True,
        "download_url": res_obj.file_url,
        "message": f"Thank you, {user_name}. Your download has been authorized!"
    })

import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@csrf_exempt
def submit_membership(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    province = (data.get('province') or '').strip()
    organization = (data.get('organization') or '').strip()
    role = (data.get('role') or '').strip()

    if not full_name or not email or not province:
        return JsonResponse({"success": False, "error": "Full Name, Email, and Province are required."}, status=400)

    m = Membership.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        province=province,
        organization=organization,
        role=role
    )

    # Email Notifications (Safely wrapped so DB record is never lost)
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hrdforum.org')
        admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', 'alerts@hrdforum.org')

        # 1. Admin Notification Email
        admin_subject = f"[NEW MEMBERSHIP APPLICATION] {m.full_name} - {m.province}"
        admin_body = (
            f"NEW MEMBERSHIP APPLICATION RECEIVED (#{m.id})\n"
            f"----------------------------------------\n"
            f"Applicant Name: {m.full_name}\n"
            f"Email: {m.email}\n"
            f"Phone: {m.phone or 'N/A'}\n"
            f"Province: {m.province}\n"
            f"Organization: {m.organization or 'N/A'}\n"
            f"Role / Designation: {m.role or 'N/A'}\n"
            f"Status: {m.get_status_display()}\n"
            f"Submitted At: {m.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"----------------------------------------\n"
            f"HRD Forum Nepal Membership Desk"
        )
        send_mail(admin_subject, admin_body, from_email, [admin_email], fail_silently=False)

        # 2. Applicant Confirmation Email
        if m.email:
            applicant_subject = "HRD Forum Nepal Membership Application Confirmation"
            applicant_body = (
                f"Dear {m.full_name},\n\n"
                f"Thank you for applying to join the Human Rights Defenders Forum (HRD Forum) Nepal network in {m.province}.\n\n"
                f"Your application (Ref #{m.id}) has been received and is currently under review by our provincial coordination team.\n\n"
                f"Application Details:\n"
                f"- Name: {m.full_name}\n"
                f"- Province: {m.province}\n"
                f"- Status: Pending Review\n\n"
                f"Our team will contact you shortly regarding the verification process.\n\n"
                f"Warm regards,\n"
                f"Human Rights Defenders Forum Nepal\n"
                f"https://hrdforum.org"
            )
            send_mail(applicant_subject, applicant_body, from_email, [m.email], fail_silently=False)

    except Exception as err:
        logger.error(f"Membership email dispatch error for ID #{m.id}: {err}")

    return JsonResponse({
        "success": True,
        "id": m.id,
        "message": "Membership application submitted successfully! Our team will contact you shortly."
    }, status=201)

@csrf_exempt
def submit_incident(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    reporter_name = (data.get('reporter_name') or '').strip()
    contact_info = (data.get('contact_info') or '').strip()
    province = (data.get('province') or '').strip()
    incident_type = (data.get('incident_type') or 'Urgent Support').strip()
    details = (data.get('details') or '').strip()
    priority = (data.get('priority') or 'High').strip()

    if not reporter_name or not contact_info or not province or not details:
        return JsonResponse({"success": False, "error": "Reporter Name, Contact Info, Province, and Details required."}, status=400)

    inc = Incident.objects.create(
        reporter_name=reporter_name,
        contact_info=contact_info,
        province=province,
        incident_type=incident_type,
        details=details,
        priority=priority
    )

    # Email Notifications (Safely wrapped so DB record is never lost)
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hrdforum.org')
        admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', 'alerts@hrdforum.org')

        # Recipient determination (Admin + Provincial Helpdesk if configured)
        recipients = [admin_email]
        prov_obj = Province.objects.filter(name__icontains=province.replace('Province', '').strip()).first()
        if prov_obj and prov_obj.helpdesk_email and prov_obj.helpdesk_email not in recipients:
            recipients.append(prov_obj.helpdesk_email)

        subject = f"[URGENT INCIDENT ALERT] {inc.incident_type} - {inc.province} (#{inc.id})"
        body = (
            f"URGENT INCIDENT REPORT RECEIVED (#{inc.id})\n"
            f"----------------------------------------\n"
            f"Incident ID: {inc.id}\n"
            f"Reporter Name: {inc.reporter_name}\n"
            f"Contact Info: {inc.contact_info}\n"
            f"Province: {inc.province}\n"
            f"Support Type / Category: {inc.incident_type}\n"
            f"Priority Level: {inc.priority}\n"
            f"Submission Timestamp: {inc.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Incident Details & Threat Description:\n"
            f"{inc.details}\n\n"
            f"----------------------------------------\n"
            f"HRD Forum Nepal Rapid Protection Desk"
        )
        send_mail(subject, body, from_email, recipients, fail_silently=False)

    except Exception as err:
        logger.error(f"Incident email dispatch error for Alert #{inc.id}: {err}")

    return JsonResponse({
        "success": True,
        "id": inc.id,
        "message": "Incident report logged securely. The regional helpdesk team has been alerted."
    }, status=201)

from functools import wraps
from django.contrib.auth import authenticate, login, logout

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            return JsonResponse({"success": False, "error": "Unauthorized access. Staff credentials required."}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ADMIN PORTAL ENDPOINTS

@csrf_exempt
def admin_login(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST
    
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    user = authenticate(request, username=username, password=password)
    if user and user.is_staff:
        login(request, user)
        return JsonResponse({"success": True, "message": "Admin authorization successful!"})
        
    return JsonResponse({"success": False, "error": "Invalid username or password credentials."}, status=401)

@csrf_exempt
def admin_logout(request):
    logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully."})

@csrf_exempt
@staff_required
def admin_news_manage(request, news_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        n = News.objects.create(
            title=data.get('title', 'News Update'),
            date_str=data.get('date_str', 'Today'),
            image_url=data.get('image_url', 'https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=500&q=80'),
            category=data.get('category', 'General'),
            summary=data.get('summary', ''),
            content=data.get('content', data.get('summary', ''))
        )
        return JsonResponse({"success": True, "id": n.id, "message": "News item published successfully!"})
    elif request.method == 'DELETE' and news_id:
        News.objects.filter(id=news_id).delete()
        return JsonResponse({"success": True, "message": "News item deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_popup_manage(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        popup = PopupConfig.objects.first()
        if not popup:
            popup = PopupConfig()
        popup.image_url = data.get('image_url', popup.image_url)
        popup.title = data.get('title', popup.title)
        popup.subtitle = data.get('subtitle', popup.subtitle)
        popup.link_url = data.get('link_url', popup.link_url)
        popup.link_text = data.get('link_text', popup.link_text)
        popup.active = bool(int(data.get('active', 1)))
        popup.save()
        return JsonResponse({"success": True, "message": "Popup configuration updated!"})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_gallery_manage(request, photo_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        g = Gallery.objects.create(
            title=data.get('title', 'Gallery Photo'),
            image_url=data.get('image_url', 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=600&q=80'),
            category=data.get('category', 'General')
        )
        return JsonResponse({"success": True, "id": g.id, "message": "Photo uploaded successfully!"})
    elif request.method == 'DELETE' and photo_id:
        Gallery.objects.filter(id=photo_id).delete()
        return JsonResponse({"success": True, "message": "Photo deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_video_manage(request, video_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        v = Video.objects.create(
            title=data.get('title', 'Video Documentary'),
            embed_url=data.get('embed_url', ''),
            category=data.get('category', 'Documentary'),
            date_str=data.get('date_str', 'Today')
        )
        return JsonResponse({"success": True, "id": v.id, "message": "Video published successfully!"})
    elif request.method == 'DELETE' and video_id:
        Video.objects.filter(id=video_id).delete()
        return JsonResponse({"success": True, "message": "Video deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_resources_manage(request, res_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        r = Resource.objects.create(
            title=data.get('title', 'Resource Document'),
            category=data.get('category', 'Document'),
            format=data.get('format', 'PDF'),
            file_size=data.get('file_size', 'PDF • 2.0 MB'),
            file_url=data.get('file_url', '#'),
            is_gated=data.get('is_gated', True)
        )
        return JsonResponse({"success": True, "id": r.id, "message": "Resource published successfully!"})
    elif request.method == 'DELETE' and res_id:
        Resource.objects.filter(id=res_id).delete()
        return JsonResponse({"success": True, "message": "Resource deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_gated_logs(request):
    leads = GatedDownloadLead.objects.all().order_by('-downloaded_at')
    res = []
    for l in leads:
        res.append({
            "id": l.id,
            "user_name": l.user_name,
            "user_email": l.user_email,
            "resource_title": l.resource_title or "Document",
            "downloaded_at": l.downloaded_at.strftime('%Y-%m-%d %H:%M') if l.downloaded_at else ""
        })
    return JsonResponse(res, safe=False)

@csrf_exempt
@staff_required
def admin_incidents_list(request):
    incidents = Incident.objects.all().order_by('-created_at')
    res = []
    for i in incidents:
        res.append({
            "id": i.id,
            "reporter_name": i.reporter_name,
            "contact_info": i.contact_info,
            "province": i.province,
            "incident_type": i.incident_type,
            "details": i.details,
            "priority": i.priority,
            "created_at": i.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse(res, safe=False)

@csrf_exempt
@staff_required
def admin_memberships_list(request):
    members = Membership.objects.all().order_by('-created_at')
    res = []
    for m in members:
        res.append({
            "id": m.id,
            "full_name": m.full_name,
            "email": m.email,
            "phone": m.phone,
            "province": m.province,
            "organization": m.organization,
            "role": m.role,
            "status": m.status,
            "created_at": m.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse(res, safe=False)

# TEAM & COLLABORATION ENDPOINTS

def api_team(request):
    category = request.GET.get('category')
    queryset = TeamMember.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    res = []
    for item in queryset:
        res.append({
            "id": item.id,
            "name": item.name,
            "designation": item.designation,
            "category": item.category,
            "bio": item.bio,
            "image_url": item.image_url,
            "order_index": item.order_index
        })
    return JsonResponse(res, safe=False)

def api_collaborations(request):
    category = request.GET.get('category')
    queryset = Collaboration.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    res = []
    for item in queryset:
        res.append({
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "logo_url": item.logo_url,
            "blurb": item.blurb,
            "website_url": item.website_url,
            "order_index": item.order_index
        })
    return JsonResponse(res, safe=False)

@csrf_exempt
@staff_required
def admin_team_manage(request, member_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        t = TeamMember.objects.create(
            name=data.get('name', 'Team Member'),
            designation=data.get('designation', 'Coordinator'),
            category=data.get('category', 'executive'),
            bio=data.get('bio', ''),
            image_url=data.get('image_url', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80'),
            order_index=int(data.get('order_index', 0))
        )
        return JsonResponse({"success": True, "id": t.id, "message": "Team member added successfully!"})
    elif request.method == 'DELETE' and member_id:
        TeamMember.objects.filter(id=member_id).delete()
        return JsonResponse({"success": True, "message": "Team member deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
@staff_required
def admin_collaborations_manage(request, collab_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = request.POST
        c = Collaboration.objects.create(
            name=data.get('name', 'Partner Organization'),
            category=data.get('category', 'institutional'),
            logo_url=data.get('logo_url', 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=400&q=80'),
            blurb=data.get('blurb', ''),
            website_url=data.get('website_url', '#'),
            order_index=int(data.get('order_index', 0))
        )
        return JsonResponse({"success": True, "id": c.id, "message": "Collaboration added successfully!"})
    elif request.method == 'DELETE' and collab_id:
        Collaboration.objects.filter(id=collab_id).delete()
        return JsonResponse({"success": True, "message": "Collaboration deleted."})
    return JsonResponse({"error": "Method not allowed"}, status=405)
