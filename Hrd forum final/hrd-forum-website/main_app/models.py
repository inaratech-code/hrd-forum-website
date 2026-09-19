from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Stats(models.Model):
    provincial_networks = models.PositiveIntegerField(default=7)
    monitored_defenders = models.PositiveIntegerField(default=1200)
    resolved_cases = models.PositiveIntegerField(default=150)
    total_visitors = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Statistics Metrics"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern (only one stats row allowed)
        if not self.pk and Stats.objects.exists():
            raise ValidationError("There can be only one Stats instance.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stats: {self.provincial_networks} Networks, {self.monitored_defenders}+ Defenders"


class UniqueVisitor(models.Model):
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=255, blank=True, default='')
    first_visited = models.DateTimeField(auto_now_add=True)
    last_visited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Unique Visitors Log"

    def __str__(self):
        return f"Unique Visitor ({self.ip_address})"


class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    base_city = models.CharField(max_length=100)
    coords_lat = models.FloatField()
    coords_lng = models.FloatField()
    coordinators_count = models.PositiveIntegerField(default=10)
    districts_count = models.PositiveIntegerField(default=10)
    helpline_phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    helpdesk_email = models.EmailField(blank=True, default='')
    active_cases = models.PositiveIntegerField(default=0)
    description = models.TextField()
    long_summary = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.base_city})"


class News(models.Model):
    title = models.CharField(max_length=255)
    published_date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.CharField(max_length=50, default='News & Updates')
    summary = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = "News & Updates"
        ordering = ['-published_date']

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def __str__(self):
        return self.title


class Resource(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, default='Document')
    format = models.CharField(max_length=20, default='PDF')
    file_size = models.CharField(max_length=50, default='2.0 MB')
    file_upload = models.FileField(upload_to='resources/', blank=True, null=True)
    file_url = models.URLField(max_length=500, blank=True, null=True)
    is_gated = models.BooleanField(default=True)

    @property
    def display_file(self):
        if self.file_upload:
            return self.file_upload.url
        return self.file_url or ''

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
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name='memberships')
    organization = models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.province.name}) - {self.get_status_display()}"


class Incident(models.Model):
    reporter_name = models.CharField(max_length=150)
    contact_info = models.CharField(max_length=200)
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name='incidents')
    incident_type = models.CharField(max_length=100, default='Urgent Support')
    details = models.TextField()
    priority = models.CharField(max_length=50, default='High')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ALERT: {self.incident_type} - {self.province.name} ({self.reporter_name})"


class PopupConfig(models.Model):
    image = models.ImageField(upload_to='popups/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True)
    link_url = models.CharField(max_length=500, default='#')
    link_text = models.CharField(max_length=100, default='Learn More')
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Homepage Popup Banners"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def __str__(self):
        return f"Popup: {self.title} ({'Active' if self.active else 'Disabled'})"


class Gallery(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    category = models.CharField(max_length=50, default='Advocacy')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Photo Gallery"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def __str__(self):
        return self.title


class Blog(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    published_date = models.DateField(default=timezone.now)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date']

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def __str__(self):
        return self.title


class Video(models.Model):
    title = models.CharField(max_length=255)
    embed_url = models.URLField(max_length=500)
    category = models.CharField(max_length=50, default='Documentary')
    published_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title


class GatedDownloadLead(models.Model):
    user_name = models.CharField(max_length=150)
    user_email = models.EmailField()
    resource = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    resource_title = models.CharField(max_length=255, blank=True, default='')
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Gated Download Leads"
        ordering = ['-downloaded_at']

    def save(self, *args, **kwargs):
        if self.resource and not self.resource_title:
            self.resource_title = self.resource.title
        super().save(*args, **kwargs)

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
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Team Members"
        ordering = ['order_index', 'id']

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Collaboration(models.Model):
    CATEGORY_CHOICES = [
        ('institutional', 'Institutional Collaboration'),
        ('individual', 'Individual Collaboration'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='institutional')
    logo = models.ImageField(upload_to='collaborations/', blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    blurb = models.TextField()
    website_url = models.URLField(max_length=500, blank=True, default='')
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Collaborations"
        ordering = ['order_index', 'id']

    @property
    def display_logo(self):
        if self.logo:
            return self.logo.url
        return self.logo_url or ''

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class NewsFlash(models.Model):
    text = models.CharField(max_length=255)
    link_url = models.URLField(max_length=500, blank=True, null=True)
    active = models.BooleanField(default=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News Flashes / Ticker"
        ordering = ['order_index', '-created_at']

    def __str__(self):
        return self.text