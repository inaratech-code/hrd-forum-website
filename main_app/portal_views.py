import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Count

from .models import (
    Gallery, Resource, Incident, Membership, News, Province,
    Stats, UniqueVisitor, Blog, Video, TeamMember, Collaboration
)
from .forms import GalleryForm, ResourceForm

logger = logging.getLogger(__name__)

def staff_required(view_func):
    """Decorator requiring staff or superuser privileges for portal routes."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.is_superuser),
        login_url='/portal/login/'
    )
    return actual_decorator(view_func)


# AUTHENTICATION VIEWS

def portal_login_view(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('portal_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! You are logged into HRD Forum Portal.")
            next_url = request.GET.get('next') or request.POST.get('next') or 'portal_dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials or insufficient permissions for portal access.")

    return render(request, 'portal/login.html')


def portal_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out of the portal.")
    return redirect('portal_login')


# PORTAL DASHBOARD OVERVIEW

@staff_required
def portal_dashboard_view(request):
    incidents_total = Incident.objects.count()
    incidents_urgent = Incident.objects.filter(priority__in=['Urgent', 'High']).count()
    memberships_pending = Membership.objects.filter(status='pending').count()
    memberships_total = Membership.objects.count()
    gallery_total = Gallery.objects.count()
    resources_total = Resource.objects.count()
    news_total = News.objects.count()
    provinces_total = Province.objects.count()

    recent_incidents = Incident.objects.order_by('-created_at')[:5]
    recent_gallery = Gallery.objects.order_by('-created_at')[:6]
    recent_memberships = Membership.objects.order_by('-created_at')[:5]

    context = {
        'kpi_incidents_total': incidents_total,
        'kpi_incidents_urgent': incidents_urgent,
        'kpi_memberships_pending': memberships_pending,
        'kpi_memberships_total': memberships_total,
        'kpi_gallery_total': gallery_total,
        'kpi_resources_total': resources_total,
        'kpi_news_total': news_total,
        'kpi_provinces_total': provinces_total,
        'recent_incidents': recent_incidents,
        'recent_gallery': recent_gallery,
        'recent_memberships': recent_memberships,
    }
    return render(request, 'portal/dashboard.html', context)


# PHOTO GALLERY CRUD VIEWS

@staff_required
def portal_gallery_list(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    photos = Gallery.objects.all()

    if query:
        photos = photos.filter(Q(title__icontains=query) | Q(category__icontains=query))

    if selected_category and selected_category != 'All':
        photos = photos.filter(category__iexact=selected_category)

    photos = photos.order_by('-created_at')

    # Categories list for filter pills
    categories = ['All', 'Advocacy', 'Fact-Finding', 'Training', 'Assemblies', 'General']

    context = {
        'photos': photos,
        'query': query,
        'selected_category': selected_category or 'All',
        'categories': categories,
        'total_count': photos.count(),
    }
    return render(request, 'portal/gallery_list.html', context)


@staff_required
def portal_gallery_add(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            messages.success(request, f"Photo '{photo.title}' added successfully to the gallery!")
            return redirect('portal_gallery_list')
        else:
            messages.error(request, "Please fix the errors in the form below.")
    else:
        form = GalleryForm()

    context = {
        'form': form,
        'title_page': 'Add Photo to Gallery',
        'is_edit': False,
    }
    return render(request, 'portal/gallery_form.html', context)


@staff_required
def portal_gallery_edit(request, photo_id):
    photo = get_object_or_404(Gallery, id=photo_id)
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            photo = form.save()
            messages.success(request, f"Gallery photo '{photo.title}' updated successfully!")
            return redirect('portal_gallery_list')
        else:
            messages.error(request, "Please fix the errors in the form below.")
    else:
        form = GalleryForm(instance=photo)

    context = {
        'form': form,
        'photo': photo,
        'title_page': f"Edit Photo: {photo.title}",
        'is_edit': True,
    }
    return render(request, 'portal/gallery_form.html', context)


@staff_required
def portal_gallery_delete(request, photo_id):
    photo = get_object_or_404(Gallery, id=photo_id)
    if request.method == 'POST':
        title = photo.title
        photo.delete()
        messages.success(request, f"Gallery photo '{title}' was deleted successfully.")
        return redirect('portal_gallery_list')

    context = {
        'photo': photo,
        'item_type': 'Photo Gallery Item',
        'item_title': photo.title,
        'cancel_url': 'portal_gallery_list'
    }
    return render(request, 'portal/confirm_delete.html', context)


# RESOURCE CRUD VIEWS

@staff_required
def portal_resource_list(request):
    query = request.GET.get('q', '').strip()
    resources = Resource.objects.all()

    if query:
        resources = resources.filter(Q(title__icontains=query) | Q(category__icontains=query))

    resources = resources.order_by('-id')

    context = {
        'resources': resources,
        'query': query,
        'total_count': resources.count(),
    }
    return render(request, 'portal/resource_list.html', context)


@staff_required
def portal_resource_add(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            res = form.save()
            messages.success(request, f"Resource '{res.title}' added successfully!")
            return redirect('portal_resource_list')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = ResourceForm()

    return render(request, 'portal/resource_form.html', {'form': form, 'is_edit': False})


@staff_required
def portal_resource_edit(request, res_id):
    res = get_object_or_404(Resource, id=res_id)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=res)
        if form.is_valid():
            res = form.save()
            messages.success(request, f"Resource '{res.title}' updated successfully!")
            return redirect('portal_resource_list')
    else:
        form = ResourceForm(instance=res)

    return render(request, 'portal/resource_form.html', {'form': form, 'resource': res, 'is_edit': True})


@staff_required
def portal_resource_delete(request, res_id):
    res = get_object_or_404(Resource, id=res_id)
    if request.method == 'POST':
        title = res.title
        res.delete()
        messages.success(request, f"Resource '{title}' deleted.")
        return redirect('portal_resource_list')
    return render(request, 'portal/confirm_delete.html', {'item_type': 'Resource Document', 'item_title': res.title, 'cancel_url': 'portal_resource_list'})


# INCIDENTS & MEMBERSHIPS VIEWS

@staff_required
def portal_incidents_list(request):
    incidents = Incident.objects.order_by('-created_at')
    return render(request, 'portal/incidents_list.html', {'incidents': incidents})


@staff_required
def portal_memberships_list(request):
    memberships = Membership.objects.order_by('-created_at')
    return render(request, 'portal/memberships_list.html', {'memberships': memberships})
