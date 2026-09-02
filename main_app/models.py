from django.db import models

class Stats(models.Model):
    provincial_networks = models.IntegerField(default=7)
    monitored_defenders = models.CharField(max_length=50, default='1,200+')
    resolved_cases = models.CharField(max_length=50, default='150+')
    total_visitors = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Statistics Metrics"

    def __str__(self):
        return f"Stats: {self.provincial_networks} Networks, {self.monitored_defenders} Defenders"


class Province(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    base_city = models.CharField(max_length=100)
    coords_lat = models.FloatField()
    coords_lng = models.FloatField()
    coordinators_count = models.IntegerField(default=10)
    helpline_phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    helpdesk_email = models.EmailField(blank=True, default='')
    active_cases = models.IntegerField(default=0)
    description = models.TextField()
    long_summary = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.base_city})"


class News(models.Model):
    title = models.CharField(max_length=255)
    date_str = models.CharField(max_length=50)
    image_url = models.URLField(max_length=500)
    category = models.CharField(max_length=50, default='News & Updates')
    summary = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = "News & Updates"

    def __str__(self):
        return self.title


class Resource(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, default='Document')
    format = models.CharField(max_length=20, default='PDF')
    file_size = models.CharField(max_length=50, default='2.0 MB')
    file_url = models.CharField(max_length=500, default='#')
    is_gated = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.format})"


class Membership(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    province = models.CharField(max_length=100)
    organization = models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.province}) - {self.get_status_display()}"


class Incident(models.Model):
    reporter_name = models.CharField(max_length=150)
    contact_info = models.CharField(max_length=200)
    province = models.CharField(max_length=100)
    incident_type = models.CharField(max_length=100, default='Urgent Support')
    details = models.TextField()
    priority = models.CharField(max_length=50, default='High')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ALERT: {self.incident_type} - {self.province} ({self.reporter_name})"


class PopupConfig(models.Model):
    image_url = models.URLField(max_length=500)
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True)
    link_url = models.CharField(max_length=500, default='#')
    link_text = models.CharField(max_length=100, default='Learn More')
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Homepage Popup Banners"

    def __str__(self):
        return f"Popup: {self.title} ({'Active' if self.active else 'Disabled'})"


class Gallery(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500)
    category = models.CharField(max_length=50, default='Advocacy')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Photo Gallery"

    def __str__(self):
        return self.title


class Blog(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    date_str = models.CharField(max_length=50)
    content = models.TextField()
    image_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Video(models.Model):
    title = models.CharField(max_length=255)
    embed_url = models.URLField(max_length=500)
    category = models.CharField(max_length=50, default='Documentary')
    date_str = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class GatedDownloadLead(models.Model):
    user_name = models.CharField(max_length=150)
    user_email = models.EmailField()
    resource_id = models.IntegerField(null=True, blank=True)
    resource_title = models.CharField(max_length=255)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Gated Download Leads"

    def __str__(self):
        return f"{self.user_name} ({self.user_email}) -> {self.resource_title}"


class TeamMember(models.Model):
    CATEGORY_CHOICES = [
        ('executive', 'Executive Team'),
        ('advisory', 'Advisory Board'),
        ('general', 'General Members'),
    ]

    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='executive')
    bio = models.TextField(blank=True, default='')
    image_url = models.URLField(max_length=500, default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80')
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Team Members"
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Collaboration(models.Model):
    CATEGORY_CHOICES = [
        ('institutional', 'Institutional Collaboration'),
        ('individual', 'Individual Collaboration'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='institutional')
    logo_url = models.URLField(max_length=500, default='https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=400&q=80')
    blurb = models.TextField()
    website_url = models.URLField(max_length=500, blank=True, default='#')
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Collaborations"
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
