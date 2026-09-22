import json
import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone

from .models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Blog, Video, GatedDownloadLead,
    TeamMember, Collaboration, NewsFlash, UniqueVisitor
, SiteSettings)

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
    except Exception as e:
        logger.warning(f"Visitor tracking failed: {e}")

def parse_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return {}
    return request.POST.dict()

# PUBLIC READ ENDPOINTS

def index_page(request):
    _track_visitor(request)
    settings = SiteSettings.objects.first()
    return render(request, 'index.html', {'settings': settings})


def about_page(request):
    _track_visitor(request)
    return render(request, 'about_page.html')


def gallery_page(request):
    _track_visitor(request)
    return render(request, 'gallery_page.html')

def news_detail_page(request, news_id):
    _track_visitor(request)
    from django.shortcuts import get_object_or_404
    news_item = get_object_or_404(News, id=news_id)
    recent_news = News.objects.exclude(id=news_id).order_by('-published_date')[:3]
    return render(request, 'news_detail_page.html', {
        'news': news_item,
        'recent_news': recent_news
    })


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /portal/",
        "Disallow: /admin/",
        "Disallow: /api/",
        "",
        "Sitemap: https://hrdforum.org/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    lastmod = timezone.now().date().isoformat()
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://hrdforum.org/</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    return HttpResponse(xml.strip(), content_type="application/xml")


def api_stats(request):
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

def api_updates(request):
    from .models import OrganizationalUpdate
    updates = OrganizationalUpdate.objects.all().order_by('-date_posted', '-id')
    data = [{
        "id": u.id,
        "title": u.title,
        "date_str": str(u.date_posted),
        "document_url": u.document_attachment.url if u.document_attachment else '',
        "description": u.description,
        "is_urgent": u.is_urgent,
    } for u in updates]
    return JsonResponse(data, safe=False)

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

# LEGACY ADMIN JSON API (retired — use /portal/)

def legacy_admin_api_disabled(request, *args, **kwargs):
    """Former static admin.html JSON API — permanently retired."""
    return JsonResponse({
        "success": False,
        "error": "This legacy admin API has been retired. Use the staff portal at /portal/."
    }, status=410)


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)

def api_site_settings(request):
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
    return JsonResponse({
        'vision_text': settings.vision_text,
        'mission_text': settings.mission_text,
        'hero_image_url': settings.hero_image.url if settings.hero_image else '',
    })

def support_page_view(request):
    settings = SiteSettings.objects.first()
    if request.method == 'POST':
        from .forms import SupportContributionForm
        form = SupportContributionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return render(request, 'support_us_page.html', {'settings': settings})
