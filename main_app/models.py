from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Stats(models.Model):
    provincial_networks = models.PositiveIntegerField(default=7)
    monitored_defenders = models.PositiveIntegerField(default=0)
    resolved_cases = models.PositiveIntegerField(default=0)
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
    cover_image = models.ImageField(upload_to='resources/covers/', blank=True, null=True)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_gated = models.BooleanField(default=True)

    @property
    def display_file(self):
        if self.file_upload:
            return self.file_upload.url
        return self.file_url or ''

    @property
    def display_cover(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url or ''

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
    joining_reason = models.TextField(blank=True, default='', verbose_name='Reason to join & support')
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
    linkedin_url = models.URLField(max_length=500, blank=True, default='')
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


class SiteSettings(models.Model):
    # About Page - Blue Hero Banner & Showcase Image
    about_hero_badge = models.CharField(max_length=150, default='ABOUT HRD FORUM NEPAL', verbose_name='About Hero Badge')
    about_hero_title = models.CharField(max_length=255, default='Protecting rights defenders and strengthening civic space across Nepal.', verbose_name='About Hero Title')
    about_hero_description = models.TextField(blank=True, default='HRD Forum Nepal connects frontline defenders, journalists, paralegals, and civil society actors with protection, legal support, and policy advocacy across all 7 provinces.', verbose_name='About Hero Description')
    about_image = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name='About Hero Showcase Image')
    about_image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='About Hero Image URL (Alternative)')
    about_image_caption = models.CharField(max_length=200, default='HRD Forum Nepal Field Network', blank=True, verbose_name='About Hero Image Caption')
    about_video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='About Hero Background Video URL')

    # About Page - Profile Section
    profile_badge = models.CharField(max_length=150, default='Coalition Profile', verbose_name='Profile Section Badge')
    profile_title = models.CharField(max_length=255, default='Profile of HRD Forum Nepal')
    profile_text = models.TextField(blank=True, default='Human Rights Defenders (HRD) Forum Nepal is a national coalition established to respond to shrinking civic space and increasing security risks faced by frontline rights defenders across Nepal.')
    profile_feature_1_title = models.CharField(max_length=200, default='National Judicial Coordination')
    profile_feature_1_text = models.TextField(blank=True, default='Bridging local human rights monitors with Supreme Court litigation support, national security funds, and emergency relocation desks.')
    profile_feature_2_title = models.CharField(max_length=200, default='7 Provincial Protection Desks')
    profile_feature_2_text = models.TextField(blank=True, default='Operating active focal helpdesks in Koshi, Madhesh, Bagmati HQ, Gandaki, Lumbini, Karnali, and Sudurpashchim provinces.')

    # About Page - Vision & Mission
    vision_title = models.CharField(max_length=150, default='Our Vision')
    vision_text = models.TextField(blank=True, default='To establish a society where human rights are respected, protected, and fulfilled for all.')
    mission_title = models.CharField(max_length=150, default='Our Mission')
    mission_text = models.TextField(blank=True, default='To protect and empower frontline human rights defenders across Nepal through legal support, capacity building, and national coordination.')

    # Landing / Home Page Configuration & Hero Photo
    hero_image = models.ImageField(upload_to='hero/', blank=True, null=True, verbose_name='Home Hero Background Image')
    hero_image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='Home Hero Image URL (Alternative)')
    home_hero_badge = models.CharField(max_length=150, default='ESTABLISHED NATIONAL HUMAN RIGHTS COALITION', verbose_name='Home Hero Badge')
    home_hero_title = models.CharField(max_length=255, default='Protecting Rights & Empowering Defenders Across Nepal', verbose_name='Home Hero Main Title')
    home_hero_subtitle = models.TextField(blank=True, default='Strengthening 7 provincial helpdesks, monitoring frontline defenders, providing 24/7 rapid response legal support, and advocating for civic safety nationwide.', verbose_name='Home Hero Subtitle')
    home_about_badge = models.CharField(max_length=150, default='ORGANIZATIONAL BACKGROUND', verbose_name='Home Overview Badge')
    home_about_title = models.CharField(max_length=200, default='About HRD Forum Nepal', verbose_name='Home Overview Title')
    home_about_text_1 = models.TextField(blank=True, default='Human Rights Defenders (HRD) Forum Nepal is a national coalition dedicated to protecting, empowering, and advocating for frontline rights defenders, journalists, paralegals, and civil society activists across Nepal. Established to respond to shrinking civic space and increasing security threats, the Forum operates as a unified shield for those facing retaliation, harassment, or legal intimidation while defending fundamental human rights.', verbose_name='Home Overview Paragraph 1')
    home_about_text_2 = models.TextField(blank=True, default='Through localized emergency assistance, continuous field monitoring, strategic legal aid, and evidence-based policy advocacy, HRD Forum Nepal bridges grassroots rights defenders with national judicial frameworks and international protection mechanisms. Our network ensures that no defender stands alone in their pursuit of justice and constitutional freedoms across all seven provinces.', verbose_name='Home Overview Paragraph 2')

    # Bank Details for Support Us Page
    bank_qr_image = models.ImageField(upload_to='bank/', blank=True, null=True)
    bank_name = models.CharField(max_length=150, default='Nepal Bank Limited')
    bank_account_name = models.CharField(max_length=150, default='HRD Forum Nepal')
    bank_account_no = models.CharField(max_length=100, default='0011223344556677')
    bank_branch = models.CharField(max_length=150, default='Kathmandu Main')

    @property
    def display_hero_image(self):
        if self.hero_image:
            return self.hero_image.url
        if self.hero_image_url:
            return self.hero_image_url
        return ''

    @property
    def display_about_image(self):
        if self.about_image:
            return self.about_image.url
        if self.about_image_url:
            return self.about_image_url
        return 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=900&q=80'

    class Meta:
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Global Site Settings'


class ThematicSector(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, default='fa-solid fa-gavel', help_text='FontAwesome icon class, e.g. fa-solid fa-gavel')
    order_index = models.IntegerField(default=0)

    class Meta:
        ordering = ['order_index', 'id']
        verbose_name_plural = 'Thematic Sectors'

    def __str__(self):
        return self.title


class SupportContribution(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    receipt_image = models.ImageField(upload_to='contributions/')
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Contribution from {self.name}"


class OrganizationalUpdate(models.Model):
    title = models.CharField(max_length=255)
    date_posted = models.DateField(default=timezone.now)
    document_attachment = models.FileField(upload_to='updates/documents/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    is_urgent = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Organizational Updates"
        ordering = ['-date_posted', '-id']

    def __str__(self):
        return self.title


class Collaboration(models.Model):
    CATEGORY_CHOICES = [
        ('institutional', 'Institutional Collaboration'),
        ('individual', 'Individual Collaboration'),
    ]
    TIER_CHOICES = [
        ('bronze', 'Bronze Level'),
        ('silver', 'Silver Level'),
        ('gold', 'Gold Level'),
        ('platinum', 'Platinum Level'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='institutional')
    support_level = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze', blank=True, null=True)
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
