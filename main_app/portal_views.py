import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group
from django.db.models import Q, Count

from .models import (
    Gallery, Resource, Incident, Membership, News, Province,
    Stats, UniqueVisitor, Blog, Video, TeamMember, Collaboration,
    NewsFlash, PopupConfig, GatedDownloadLead
)
from .forms import (
    GalleryForm, ResourceForm, NewsForm, ProvinceForm, MembershipForm,
    IncidentForm, PopupConfigForm, BlogForm, VideoForm, TeamMemberForm,
    CollaborationForm, NewsFlashForm, UserForm, GroupForm
)

logger = logging.getLogger(__name__)

def staff_required(view_func):
    """Decorator requiring staff or superuser privileges for portal routes."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.is_superuser),
        login_url='/portal/login/'
    )
    return actual_decorator(view_func)


def superuser_required(view_func):
    """Decorator requiring superuser privileges for admin user/group management."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
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
    users_total = User.objects.count()

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
        'kpi_users_total': users_total,
        'recent_incidents': recent_incidents,
        'recent_gallery': recent_gallery,
        'recent_memberships': recent_memberships,
    }
    return render(request, 'portal/dashboard.html', context)


# PHOTO GALLERY CRUD

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
    categories = ['All', 'Advocacy', 'Fact-Finding', 'Training', 'Assemblies', 'General']

    context = {
        'photos': photos,
        'query': query,
        'selected_category': selected_category or 'All',
        'categories': categories,
    }
    return render(request, 'portal/gallery_list.html', context)


@staff_required
def portal_gallery_add(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            messages.success(request, f"Photo '{photo.title}' added successfully!")
            return redirect('portal_gallery_list')
        else:
            messages.error(request, "Failed to add photo. Please check form inputs.")
    else:
        form = GalleryForm()

    return render(request, 'portal/gallery_form.html', {'form': form, 'is_edit': False})


@staff_required
def portal_gallery_edit(request, photo_id):
    photo = get_object_or_404(Gallery, id=photo_id)
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Photo '{photo.title}' updated successfully!")
            return redirect('portal_gallery_list')
        else:
            messages.error(request, "Failed to update photo. Please check inputs.")
    else:
        form = GalleryForm(instance=photo)

    return render(request, 'portal/gallery_form.html', {'form': form, 'photo': photo, 'is_edit': True})


@staff_required
def portal_gallery_delete(request, photo_id):
    photo = get_object_or_404(Gallery, id=photo_id)
    if request.method == 'POST':
        title = photo.title
        photo.delete()
        messages.success(request, f"Photo '{title}' has been deleted.")
        return redirect('portal_gallery_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': photo.title,
        'item_type': 'Photo Gallery Item',
        'cancel_url': 'portal_gallery_list'
    })


# RESOURCES CRUD

@staff_required
def portal_resource_list(request):
    query = request.GET.get('q', '').strip()
    resources = Resource.objects.all()

    if query:
        resources = resources.filter(Q(title__icontains=query) | Q(category__icontains=query) | Q(format__icontains=query))

    resources = resources.order_by('-id')

    context = {
        'resources': resources,
        'query': query,
    }
    return render(request, 'portal/resource_list.html', context)


@staff_required
def portal_resource_add(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save()
            messages.success(request, f"Resource '{resource.title}' uploaded successfully!")
            return redirect('portal_resource_list')
        else:
            messages.error(request, "Failed to create resource. Please review errors.")
    else:
        form = ResourceForm()

    return render(request, 'portal/resource_form.html', {'form': form, 'is_edit': False})


@staff_required
def portal_resource_edit(request, res_id):
    resource = get_object_or_404(Resource, id=res_id)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, f"Resource '{resource.title}' updated successfully!")
            return redirect('portal_resource_list')
        else:
            messages.error(request, "Failed to update resource. Please review errors.")
    else:
        form = ResourceForm(instance=resource)

    return render(request, 'portal/resource_form.html', {'form': form, 'resource': resource, 'is_edit': True})


@staff_required
def portal_resource_delete(request, res_id):
    resource = get_object_or_404(Resource, id=res_id)
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f"Resource '{title}' deleted successfully.")
        return redirect('portal_resource_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': resource.title,
        'item_type': 'Document Resource',
        'cancel_url': 'portal_resource_list'
    })


# INCIDENTS MANAGEMENT

@staff_required
def portal_incidents_list(request):
    query = request.GET.get('q', '').strip()
    priority = request.GET.get('priority', '').strip()

    incidents = Incident.objects.select_related('province').all()

    if query:
        incidents = incidents.filter(
            Q(reporter_name__icontains=query) |
            Q(contact_info__icontains=query) |
            Q(incident_type__icontains=query) |
            Q(details__icontains=query)
        )

    if priority and priority != 'All':
        incidents = incidents.filter(priority__iexact=priority)

    incidents = incidents.order_by('-created_at')

    context = {
        'incidents': incidents,
        'query': query,
        'selected_priority': priority or 'All',
        'priorities': ['All', 'High', 'Urgent', 'Medium', 'Low'],
    }
    return render(request, 'portal/incidents_list.html', context)


@staff_required
def portal_incident_add(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            messages.success(request, f"Incident report for '{incident.reporter_name}' created.")
            return redirect('portal_incidents_list')
        else:
            messages.error(request, "Failed to create incident report.")
    else:
        form = IncidentForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Create Incident Alert',
        'subtitle': 'Record a new emergency incident report',
        'back_url': 'portal_incidents_list'
    })


@staff_required
def portal_incident_edit(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, f"Incident alert #{incident.id} updated.")
            return redirect('portal_incidents_list')
        else:
            messages.error(request, "Failed to update incident alert.")
    else:
        form = IncidentForm(instance=incident)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': f'Edit Incident Alert #{incident.id}',
        'subtitle': f'Reporter: {incident.reporter_name}',
        'back_url': 'portal_incidents_list'
    })


@staff_required
def portal_incident_delete(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    if request.method == 'POST':
        incident.delete()
        messages.success(request, f"Incident alert #{incident_id} deleted.")
        return redirect('portal_incidents_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': f"Incident #{incident.id} - {incident.reporter_name}",
        'item_type': 'Incident Alert',
        'cancel_url': 'portal_incidents_list'
    })


# MEMBERSHIPS MANAGEMENT

@staff_required
def portal_memberships_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    memberships = Membership.objects.select_related('province').all()

    if query:
        memberships = memberships.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(organization__icontains=query) |
            Q(role__icontains=query)
        )

    if status and status != 'All':
        memberships = memberships.filter(status__iexact=status)

    memberships = memberships.order_by('-created_at')

    context = {
        'memberships': memberships,
        'query': query,
        'selected_status': status or 'All',
        'statuses': ['All', 'pending', 'approved', 'rejected'],
    }
    return render(request, 'portal/memberships_list.html', context)


@staff_required
def portal_membership_add(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Membership application for '{member.full_name}' recorded.")
            return redirect('portal_memberships_list')
        else:
            messages.error(request, "Failed to save membership application.")
    else:
        form = MembershipForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Member Application',
        'subtitle': 'Create a new defender membership record',
        'back_url': 'portal_memberships_list'
    })


@staff_required
def portal_membership_edit(request, member_id):
    member = get_object_or_404(Membership, id=member_id)
    if request.method == 'POST':
        form = MembershipForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"Membership record for '{member.full_name}' updated.")
            return redirect('portal_memberships_list')
        else:
            messages.error(request, "Failed to update membership record.")
    else:
        form = MembershipForm(instance=member)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': f'Edit Member Application',
        'subtitle': member.full_name,
        'back_url': 'portal_memberships_list'
    })


@staff_required
def portal_membership_approve(request, member_id):
    member = get_object_or_404(Membership, id=member_id)
    member.status = 'approved'
    member.save()
    messages.success(request, f"Membership for '{member.full_name}' approved successfully!")
    return redirect('portal_memberships_list')


@staff_required
def portal_membership_reject(request, member_id):
    member = get_object_or_404(Membership, id=member_id)
    member.status = 'rejected'
    member.save()
    messages.warning(request, f"Membership for '{member.full_name}' set to rejected.")
    return redirect('portal_memberships_list')


@staff_required
def portal_membership_delete(request, member_id):
    member = get_object_or_404(Membership, id=member_id)
    if request.method == 'POST':
        name = member.full_name
        member.delete()
        messages.success(request, f"Membership record for '{name}' deleted.")
        return redirect('portal_memberships_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': member.full_name,
        'item_type': 'Membership Application',
        'cancel_url': 'portal_memberships_list'
    })


# NEWS & UPDATES CRUD

@staff_required
def portal_news_list(request):
    query = request.GET.get('q', '').strip()
    news_items = News.objects.all()

    if query:
        news_items = news_items.filter(Q(title__icontains=query) | Q(category__icontains=query) | Q(summary__icontains=query))

    news_items = news_items.order_by('-published_date')

    return render(request, 'portal/generic_list.html', {
        'items': news_items,
        'query': query,
        'title': 'News & Updates',
        'module_slug': 'news',
        'headers': ['Title', 'Category', 'Published Date', 'Summary'],
        'fields': ['title', 'category', 'published_date', 'summary'],
        'add_url': 'portal_news_add',
        'edit_url_name': 'portal_news_edit',
        'delete_url_name': 'portal_news_delete',
    })


@staff_required
def portal_news_add(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"News article '{item.title}' published!")
            return redirect('portal_news_list')
        else:
            messages.error(request, "Failed to publish news article.")
    else:
        form = NewsForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Publish News Article',
        'subtitle': 'Add a new press release or rights bulletin',
        'back_url': 'portal_news_list'
    })


@staff_required
def portal_news_edit(request, item_id):
    item = get_object_or_404(News, id=item_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"News article '{item.title}' updated.")
            return redirect('portal_news_list')
        else:
            messages.error(request, "Failed to update news article.")
    else:
        form = NewsForm(instance=item)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit News Article',
        'subtitle': item.title,
        'back_url': 'portal_news_list'
    })


@staff_required
def portal_news_delete(request, item_id):
    item = get_object_or_404(News, id=item_id)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f"News article '{title}' deleted.")
        return redirect('portal_news_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': item.title,
        'item_type': 'News Article',
        'cancel_url': 'portal_news_list'
    })


# PROVINCES CRUD

@staff_required
def portal_province_list(request):
    query = request.GET.get('q', '').strip()
    provinces = Province.objects.all()

    if query:
        provinces = provinces.filter(Q(name__icontains=query) | Q(base_city__icontains=query) | Q(code__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': provinces,
        'query': query,
        'title': 'Provincial Desks Directory',
        'module_slug': 'provinces',
        'headers': ['Name', 'Code', 'Base City', 'Coordinators', 'Active Cases'],
        'fields': ['name', 'code', 'base_city', 'coordinators_count', 'active_cases'],
        'add_url': 'portal_province_add',
        'edit_url_name': 'portal_province_edit',
        'delete_url_name': 'portal_province_delete',
    })


@staff_required
def portal_province_add(request):
    if request.method == 'POST':
        form = ProvinceForm(request.POST)
        if form.is_valid():
            prov = form.save()
            messages.success(request, f"Province '{prov.name}' added.")
            return redirect('portal_province_list')
        else:
            messages.error(request, "Failed to add province.")
    else:
        form = ProvinceForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Provincial Desk',
        'subtitle': 'Create a new provincial directory entry',
        'back_url': 'portal_province_list'
    })


@staff_required
def portal_province_edit(request, prov_id):
    prov = get_object_or_404(Province, id=prov_id)
    if request.method == 'POST':
        form = ProvinceForm(request.POST, instance=prov)
        if form.is_valid():
            form.save()
            messages.success(request, f"Province '{prov.name}' updated.")
            return redirect('portal_province_list')
        else:
            messages.error(request, "Failed to update province.")
    else:
        form = ProvinceForm(instance=prov)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Provincial Desk',
        'subtitle': prov.name,
        'back_url': 'portal_province_list'
    })


@staff_required
def portal_province_delete(request, prov_id):
    prov = get_object_or_404(Province, id=prov_id)
    if request.method == 'POST':
        name = prov.name
        prov.delete()
        messages.success(request, f"Province '{name}' deleted.")
        return redirect('portal_province_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': prov.name,
        'item_type': 'Provincial Desk',
        'cancel_url': 'portal_province_list'
    })


# TEAM MEMBERS CRUD

@staff_required
def portal_team_list(request):
    query = request.GET.get('q', '').strip()
    team = TeamMember.objects.all()

    if query:
        team = team.filter(Q(name__icontains=query) | Q(designation__icontains=query) | Q(category__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': team,
        'query': query,
        'title': 'Team Members',
        'module_slug': 'team',
        'headers': ['Name', 'Designation', 'Category', 'Order'],
        'fields': ['name', 'designation', 'category', 'order_index'],
        'add_url': 'portal_team_add',
        'edit_url_name': 'portal_team_edit',
        'delete_url_name': 'portal_team_delete',
    })


@staff_required
def portal_team_add(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Team member '{member.name}' added.")
            return redirect('portal_team_list')
        else:
            messages.error(request, "Failed to add team member.")
    else:
        form = TeamMemberForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Team Member',
        'subtitle': 'Executive, advisory board, or general member',
        'back_url': 'portal_team_list'
    })


@staff_required
def portal_team_edit(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"Team member '{member.name}' updated.")
            return redirect('portal_team_list')
        else:
            messages.error(request, "Failed to update team member.")
    else:
        form = TeamMemberForm(instance=member)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Team Member',
        'subtitle': member.name,
        'back_url': 'portal_team_list'
    })


@staff_required
def portal_team_delete(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)
    if request.method == 'POST':
        name = member.name
        member.delete()
        messages.success(request, f"Team member '{name}' deleted.")
        return redirect('portal_team_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': member.name,
        'item_type': 'Team Member',
        'cancel_url': 'portal_team_list'
    })


# BLOGS CRUD

@staff_required
def portal_blog_list(request):
    query = request.GET.get('q', '').strip()
    blogs = Blog.objects.all()

    if query:
        blogs = blogs.filter(Q(title__icontains=query) | Q(author__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': blogs,
        'query': query,
        'title': 'Blog Articles',
        'module_slug': 'blogs',
        'headers': ['Title', 'Author', 'Published Date'],
        'fields': ['title', 'author', 'published_date'],
        'add_url': 'portal_blog_add',
        'edit_url_name': 'portal_blog_edit',
        'delete_url_name': 'portal_blog_delete',
    })


@staff_required
def portal_blog_add(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save()
            messages.success(request, f"Blog '{blog.title}' published.")
            return redirect('portal_blog_list')
        else:
            messages.error(request, "Failed to publish blog.")
    else:
        form = BlogForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Publish Blog Post',
        'subtitle': 'Write a blog or opinion piece',
        'back_url': 'portal_blog_list'
    })


@staff_required
def portal_blog_edit(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, f"Blog '{blog.title}' updated.")
            return redirect('portal_blog_list')
        else:
            messages.error(request, "Failed to update blog.")
    else:
        form = BlogForm(instance=blog)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Blog Post',
        'subtitle': blog.title,
        'back_url': 'portal_blog_list'
    })


@staff_required
def portal_blog_delete(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        title = blog.title
        blog.delete()
        messages.success(request, f"Blog '{title}' deleted.")
        return redirect('portal_blog_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': blog.title,
        'item_type': 'Blog Post',
        'cancel_url': 'portal_blog_list'
    })


# VIDEOS CRUD

@staff_required
def portal_video_list(request):
    query = request.GET.get('q', '').strip()
    videos = Video.objects.all()

    if query:
        videos = videos.filter(Q(title__icontains=query) | Q(category__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': videos,
        'query': query,
        'title': 'Video Media Library',
        'module_slug': 'videos',
        'headers': ['Title', 'Category', 'Embed URL', 'Published Date'],
        'fields': ['title', 'category', 'embed_url', 'published_date'],
        'add_url': 'portal_video_add',
        'edit_url_name': 'portal_video_edit',
        'delete_url_name': 'portal_video_delete',
    })


@staff_required
def portal_video_add(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save()
            messages.success(request, f"Video '{video.title}' added.")
            return redirect('portal_video_list')
        else:
            messages.error(request, "Failed to add video.")
    else:
        form = VideoForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Video Entry',
        'subtitle': 'Embed YouTube / Vimeo documentary video',
        'back_url': 'portal_video_list'
    })


@staff_required
def portal_video_edit(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, f"Video '{video.title}' updated.")
            return redirect('portal_video_list')
        else:
            messages.error(request, "Failed to update video.")
    else:
        form = VideoForm(instance=video)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Video Entry',
        'subtitle': video.title,
        'back_url': 'portal_video_list'
    })


@staff_required
def portal_video_delete(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        title = video.title
        video.delete()
        messages.success(request, f"Video '{title}' deleted.")
        return redirect('portal_video_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': video.title,
        'item_type': 'Video Entry',
        'cancel_url': 'portal_video_list'
    })


# COLLABORATIONS CRUD

@staff_required
def portal_collaboration_list(request):
    query = request.GET.get('q', '').strip()
    collabs = Collaboration.objects.all()

    if query:
        collabs = collabs.filter(Q(name__icontains=query) | Q(category__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': collabs,
        'query': query,
        'title': 'Partners & Collaborations',
        'module_slug': 'collaborations',
        'headers': ['Partner Name', 'Category', 'Website URL', 'Order'],
        'fields': ['name', 'category', 'website_url', 'order_index'],
        'add_url': 'portal_collaboration_add',
        'edit_url_name': 'portal_collaboration_edit',
        'delete_url_name': 'portal_collaboration_delete',
    })


@staff_required
def portal_collaboration_add(request):
    if request.method == 'POST':
        form = CollaborationForm(request.POST, request.FILES)
        if form.is_valid():
            collab = form.save()
            messages.success(request, f"Partner '{collab.name}' added.")
            return redirect('portal_collaboration_list')
        else:
            messages.error(request, "Failed to add partner collaboration.")
    else:
        form = CollaborationForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Partner Collaboration',
        'subtitle': 'Institutional or individual partner',
        'back_url': 'portal_collaboration_list'
    })


@staff_required
def portal_collaboration_edit(request, collab_id):
    collab = get_object_or_404(Collaboration, id=collab_id)
    if request.method == 'POST':
        form = CollaborationForm(request.POST, request.FILES, instance=collab)
        if form.is_valid():
            form.save()
            messages.success(request, f"Partner '{collab.name}' updated.")
            return redirect('portal_collaboration_list')
        else:
            messages.error(request, "Failed to update partner collaboration.")
    else:
        form = CollaborationForm(instance=collab)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Partner Collaboration',
        'subtitle': collab.name,
        'back_url': 'portal_collaboration_list'
    })


@staff_required
def portal_collaboration_delete(request, collab_id):
    collab = get_object_or_404(Collaboration, id=collab_id)
    if request.method == 'POST':
        name = collab.name
        collab.delete()
        messages.success(request, f"Partner '{name}' deleted.")
        return redirect('portal_collaboration_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': collab.name,
        'item_type': 'Partner Collaboration',
        'cancel_url': 'portal_collaboration_list'
    })


# NEWS FLASHES / TICKER CRUD

@staff_required
def portal_news_flash_list(request):
    query = request.GET.get('q', '').strip()
    flashes = NewsFlash.objects.all()

    if query:
        flashes = flashes.filter(Q(text__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': flashes,
        'query': query,
        'title': 'News Flashes / Ticker',
        'module_slug': 'news-flashes',
        'headers': ['Text', 'Active', 'Order', 'Link URL'],
        'fields': ['text', 'active', 'order_index', 'link_url'],
        'add_url': 'portal_news_flash_add',
        'edit_url_name': 'portal_news_flash_edit',
        'delete_url_name': 'portal_news_flash_delete',
    })


@staff_required
def portal_news_flash_add(request):
    if request.method == 'POST':
        form = NewsFlashForm(request.POST)
        if form.is_valid():
            flash = form.save()
            messages.success(request, f"Ticker flash item added.")
            return redirect('portal_news_flash_list')
        else:
            messages.error(request, "Failed to add ticker flash item.")
    else:
        form = NewsFlashForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add News Ticker Item',
        'subtitle': 'Short headline announcement for header ticker',
        'back_url': 'portal_news_flash_list'
    })


@staff_required
def portal_news_flash_edit(request, flash_id):
    flash = get_object_or_404(NewsFlash, id=flash_id)
    if request.method == 'POST':
        form = NewsFlashForm(request.POST, instance=flash)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ticker flash item updated.")
            return redirect('portal_news_flash_list')
        else:
            messages.error(request, "Failed to update ticker flash item.")
    else:
        form = NewsFlashForm(instance=flash)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit News Ticker Item',
        'subtitle': flash.text,
        'back_url': 'portal_news_flash_list'
    })


@staff_required
def portal_news_flash_delete(request, flash_id):
    flash = get_object_or_404(NewsFlash, id=flash_id)
    if request.method == 'POST':
        flash.delete()
        messages.success(request, f"Ticker flash item deleted.")
        return redirect('portal_news_flash_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': flash.text,
        'item_type': 'News Ticker Flash',
        'cancel_url': 'portal_news_flash_list'
    })


# POPUP CONFIG CRUD

@staff_required
def portal_popup_list(request):
    query = request.GET.get('q', '').strip()
    popups = PopupConfig.objects.all()

    if query:
        popups = popups.filter(Q(title__icontains=query) | Q(subtitle__icontains=query))

    return render(request, 'portal/generic_list.html', {
        'items': popups,
        'query': query,
        'title': 'Homepage Popup Banners',
        'module_slug': 'popups',
        'headers': ['Title', 'Subtitle', 'Active', 'Link Text'],
        'fields': ['title', 'subtitle', 'active', 'link_text'],
        'add_url': 'portal_popup_add',
        'edit_url_name': 'portal_popup_edit',
        'delete_url_name': 'portal_popup_delete',
    })


@staff_required
def portal_popup_add(request):
    if request.method == 'POST':
        form = PopupConfigForm(request.POST, request.FILES)
        if form.is_valid():
            popup = form.save()
            messages.success(request, f"Popup banner '{popup.title}' created.")
            return redirect('portal_popup_list')
        else:
            messages.error(request, "Failed to create popup banner.")
    else:
        form = PopupConfigForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Create Homepage Popup Banner',
        'subtitle': 'Modal banner overlay on homepage load',
        'back_url': 'portal_popup_list'
    })


@staff_required
def portal_popup_edit(request, popup_id):
    popup = get_object_or_404(PopupConfig, id=popup_id)
    if request.method == 'POST':
        form = PopupConfigForm(request.POST, request.FILES, instance=popup)
        if form.is_valid():
            form.save()
            messages.success(request, f"Popup banner '{popup.title}' updated.")
            return redirect('portal_popup_list')
        else:
            messages.error(request, "Failed to update popup banner.")
    else:
        form = PopupConfigForm(instance=popup)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Homepage Popup Banner',
        'subtitle': popup.title,
        'back_url': 'portal_popup_list'
    })


@staff_required
def portal_popup_delete(request, popup_id):
    popup = get_object_or_404(PopupConfig, id=popup_id)
    if request.method == 'POST':
        title = popup.title
        popup.delete()
        messages.success(request, f"Popup banner '{title}' deleted.")
        return redirect('portal_popup_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': popup.title,
        'item_type': 'Homepage Popup Banner',
        'cancel_url': 'portal_popup_list'
    })


# GATED DOWNLOAD LEADS

@staff_required
def portal_gated_leads_list(request):
    query = request.GET.get('q', '').strip()
    leads = GatedDownloadLead.objects.select_related('resource').all()

    if query:
        leads = leads.filter(
            Q(user_name__icontains=query) |
            Q(user_email__icontains=query) |
            Q(resource_title__icontains=query)
        )

    leads = leads.order_by('-downloaded_at')

    return render(request, 'portal/generic_list.html', {
        'items': leads,
        'query': query,
        'title': 'Gated Document Download Leads',
        'module_slug': 'gated-leads',
        'headers': ['User Name', 'Email', 'Resource Title', 'Downloaded At'],
        'fields': ['user_name', 'user_email', 'resource_title', 'downloaded_at'],
        'hide_add_button': True,
    })


# USERS & GROUPS MANAGEMENT

@superuser_required
def portal_user_list(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    users = users.order_by('-date_joined')

    return render(request, 'portal/generic_list.html', {
        'items': users,
        'query': query,
        'title': 'User Accounts & Access Control',
        'module_slug': 'users',
        'headers': ['Username', 'Email', 'Is Staff', 'Is Superuser', 'Is Active'],
        'fields': ['username', 'email', 'is_staff', 'is_superuser', 'is_active'],
        'add_url': 'portal_user_add',
        'edit_url_name': 'portal_user_edit',
        'delete_url_name': 'portal_user_delete',
    })


@superuser_required
def portal_user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            usr = form.save()
            messages.success(request, f"User account '{usr.username}' created.")
            return redirect('portal_user_list')
        else:
            messages.error(request, "Failed to create user account.")
    else:
        form = UserForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Create User Account',
        'subtitle': 'Add a staff or administrator account',
        'back_url': 'portal_user_list'
    })


@superuser_required
def portal_user_edit(request, user_id):
    usr = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=usr)
        if form.is_valid():
            form.save()
            messages.success(request, f"User account '{usr.username}' updated.")
            return redirect('portal_user_list')
        else:
            messages.error(request, "Failed to update user account.")
    else:
        form = UserForm(instance=usr)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit User Account',
        'subtitle': usr.username,
        'back_url': 'portal_user_list'
    })


@superuser_required
def portal_user_delete(request, user_id):
    usr = get_object_or_404(User, id=user_id)
    if usr.id == request.user.id:
        messages.error(request, "You cannot delete your own active session account.")
        return redirect('portal_user_list')

    if request.method == 'POST':
        username = usr.username
        usr.delete()
        messages.success(request, f"User account '{username}' deleted.")
        return redirect('portal_user_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': usr.username,
        'item_type': 'User Account',
        'cancel_url': 'portal_user_list'
    })


@superuser_required
def portal_group_list(request):
    query = request.GET.get('q', '').strip()
    groups = Group.objects.all()

    if query:
        groups = groups.filter(name__icontains=query)

    return render(request, 'portal/generic_list.html', {
        'items': groups,
        'query': query,
        'title': 'User Groups & Roles',
        'module_slug': 'groups',
        'headers': ['Group Name', 'Members Count'],
        'fields': ['name', 'id'],
        'add_url': 'portal_group_add',
        'edit_url_name': 'portal_group_edit',
        'delete_url_name': 'portal_group_delete',
    })


@superuser_required
def portal_group_add(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            grp = form.save()
            messages.success(request, f"Group '{grp.name}' created.")
            return redirect('portal_group_list')
        else:
            messages.error(request, "Failed to create group.")
    else:
        form = GroupForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Create Group Role',
        'subtitle': 'Define a role group for permission mapping',
        'back_url': 'portal_group_list'
    })


@superuser_required
def portal_group_edit(request, group_id):
    grp = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=grp)
        if form.is_valid():
            form.save()
            messages.success(request, f"Group '{grp.name}' updated.")
            return redirect('portal_group_list')
        else:
            messages.error(request, "Failed to update group.")
    else:
        form = GroupForm(instance=grp)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Edit Group Role',
        'subtitle': grp.name,
        'back_url': 'portal_group_list'
    })


@superuser_required
def portal_group_delete(request, group_id):
    grp = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        name = grp.name
        grp.delete()
        messages.success(request, f"Group '{name}' deleted.")
        return redirect('portal_group_list')

    return render(request, 'portal/confirm_delete.html', {
        'object_title': grp.name,
        'item_type': 'Group Role',
        'cancel_url': 'portal_group_list'
    })

