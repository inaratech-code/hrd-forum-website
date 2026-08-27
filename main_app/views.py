from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Blog, Video, GatedDownloadLead
)

def index_page(request):
    return render(request, 'index.html')

def api_stats(request):
    stats = Stats.objects.first()
    if stats:
        return JsonResponse({
            "provincial_networks": stats.provincial_networks,
            "monitored_defenders": stats.monitored_defenders,
            "resolved_cases": stats.resolved_cases,
            "total_visitors": stats.total_visitors,
        })
    return JsonResponse({
        "provincial_networks": 7,
        "monitored_defenders": "1,200+",
        "resolved_cases": "150+",
        "total_visitors": 14230
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
        "summary": n.summary
    } for n in news_items]
    return JsonResponse(data, safe=False)

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

    return JsonResponse({
        "success": True,
        "id": inc.id,
        "message": "Incident report logged securely. The regional helpdesk team has been alerted."
    }, status=201)
