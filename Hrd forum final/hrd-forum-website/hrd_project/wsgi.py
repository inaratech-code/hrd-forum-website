import os
from datetime import date
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrd_project.settings')

application = get_wsgi_application()


def _maybe_bootstrap():
    """Lightweight first-boot seed. Migrations stay off the request path for speed."""
    from django.core.management import call_command
    call_command('migrate', interactive=False)

    from django.conf import settings as django_settings
    from django.contrib.auth.password_validation import validate_password
    from django.contrib.auth.models import User
    from django.core.exceptions import ImproperlyConfigured, ValidationError
    from main_app.models import (
        Stats, Province, News, Resource, PopupConfig, Gallery,
        TeamMember, Collaboration, Video,
    )

    # Fast path: already seeded — avoid extra work on every cold start.
    if Stats.objects.exists() and User.objects.filter(username='Superadmin').exists():
        return

    if not User.objects.filter(username='Superadmin').exists():
        admin_pass = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()
        if not admin_pass:
            raise ImproperlyConfigured(
                "Set DJANGO_SUPERUSER_PASSWORD to a strong password before creating the initial admin."
            )
        try:
            validate_password(admin_pass, User(username='Superadmin', email='admin@hrdforum.org'))
        except ValidationError as exc:
            raise ImproperlyConfigured(
                "DJANGO_SUPERUSER_PASSWORD does not meet the configured password policy."
            ) from exc
        User.objects.create_superuser('Superadmin', 'admin@hrdforum.org', admin_pass)

    if not Stats.objects.exists():
        Stats.objects.create(
            provincial_networks=7,
            monitored_defenders=1200,
            resolved_cases=150,
            total_visitors=0
        )

    if not PopupConfig.objects.exists():
        PopupConfig.objects.create(
            image_url='https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=800&q=80',
            title='National Human Rights Defenders Convention 2026',
            subtitle='Join regional coordinators and international legal observers in Kathmandu this September.',
            link_url='#',
            link_text='Register Online Now',
            active=True
        )

    if not Province.objects.exists():
        provinces_data = [
            ('Koshi Province Desk', 'p1', 'Biratnagar', 26.4525, 87.2718, 12, '+977-21-524100', 'Main Road, Ward No. 4, Biratnagar', 14, 14,
             '12 localized monitoring human rights coordinators processing regional case interventions.',
             'The Koshi Helpdesk actively coordinates legal aid and emergency relocation across 14 Eastern districts, protecting environmental and indigenous community advocates.'),
            ('Madhesh Province Desk', 'p2', 'Janakpur', 26.7288, 85.9254, 15, '+977-41-520330', 'Station Road, Janakpurdham', 22, 8,
             'High-density advocacy missions protecting localized civil advocates.',
             'Monitors gender-based violence, election observers, and grassroots paralegals in dense border corridor districts.'),
            ('Bagmati Province Desk (Central HQ)', 'p3', 'Kathmandu HQ', 27.6939, 85.3340, 20, '+977-01-55511400', 'Thapagaun, New Baneshwor, Kathmandu', 35, 13,
             'Integrating central judicial lobbying with operational rapid response desks.',
             'Serves as the national command hub integrating Supreme Court litigation support, diplomatic liaison, and emergency security funds.'),
            ('Gandaki Province Desk', 'p4', 'Pokhara', 28.2096, 83.9856, 10, '+977-61-532190', 'New Road, Pokhara', 9, 11,
             'Active focal points monitoring environmental and land rights defenders.',
             'Specializes in safeguarding eco-defenders, conservationists, and indigenous river basin advocates against illegal resource extraction harassment.'),
            ('Lumbini Province Desk', 'p5', 'Butwal', 27.7006, 83.4484, 14, '+977-71-540220', 'Traffic Chowk, Butwal', 18, 12,
             'Cross-border coordination units assisting community paralegals.',
             'Monitors labor rights advocates, border migrant safety, and community legal aid networks across Lumbini province.'),
            ('Karnali Province Desk', 'p6', 'Surkhet', 28.6019, 81.6348, 8, '+977-83-521090', 'Birendranagar, Surkhet', 11, 10,
             'Remote-access defender support networks covering highland jurisdictions.',
             'Deploys satellite-linked emergency communication units for remote mountain defenders facing geographic isolation.'),
            ('Sudurpashchim Province Desk', 'p7', 'Dhangadhi', 28.6852, 80.5940, 11, '+977-91-523410', 'Main Bazaar, Dhangadhi', 13, 9,
             'Grassroots protective action programs for marginalized legal representatives.',
             'Focuses on protecting Dalit rights defenders, anti-caste discrimination campaigners, and rural legal assistants.')
        ]
        for p in provinces_data:
            Province.objects.create(
                name=p[0], code=p[1], base_city=p[2], coords_lat=p[3], coords_lng=p[4],
                coordinators_count=p[5], helpline_phone=p[6], address=p[7], active_cases=p[8],
                districts_count=p[9], description=p[10], long_summary=p[11]
            )

    if not News.objects.exists():
        News.objects.create(
            title='HRD Forum Launches Provincial Safety Monitoring Initiative',
            published_date=date(2025, 10, 12),
            image_url='https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=500&q=80',
            category='Safety',
            summary='Establishing 24/7 hotline desks across Koshi and Madhesh provinces.',
            content='HRD Forum Nepal has established dedicated 24/7 response mechanisms and local monitoring focal points.'
        )
        News.objects.create(
            title='New Policy Guidelines Released for Defender Protection',
            published_date=date(2025, 9, 28),
            image_url='https://images.unsplash.com/photo-1450133064473-71024230f91b?w=500&q=80',
            category='Policy',
            summary='Legal framework blueprint presented to parliament for civic space protection.',
            content='Comprehensive protection guidelines were presented to parliamentary committees for constitutional review.'
        )
        News.objects.create(
            title='National Defender Assembly Concludes in Kathmandu',
            published_date=date(2025, 8, 15),
            image_url='https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=500&q=80',
            category='Assembly',
            summary='Over 300 regional delegates aligned on security protocols.',
            content='Frontline defenders gathered at the central assembly to draft standard emergency operating protocols.'
        )

    if not Gallery.objects.exists():
        Gallery.objects.create(title='National Convention Keynote Speech', image_url='https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=600&q=80', category='Assemblies')
        Gallery.objects.create(title='Provincial Legal Workshop in Janakpur', image_url='https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=600&q=80', category='Training')
        Gallery.objects.create(title='Grassroots Fact-Finding Mission in Karnali', image_url='https://images.unsplash.com/photo-1450133064473-71024230f91b?w=600&q=80', category='Fact-Finding')

    if not Resource.objects.exists():
        Resource.objects.create(title='Annual Protection Status Report 2025', category='Report', format='PDF', file_size='4.2 MB', file_url='#', is_gated=True)
        Resource.objects.create(title='Strategic Plan 2026–2030 Blueprint', category='Publication', format='PDF', file_size='2.8 MB', file_url='#', is_gated=True)
        Resource.objects.create(title='Grassroots Security & Digital Safety Manual', category='By-Laws', format='PDF', file_size='3.5 MB', file_url='#', is_gated=False)

    if not TeamMember.objects.exists():
        TeamMember.objects.create(name='Adv. Sunita Shrestha', designation='Executive Director', category='executive', bio='Lead human rights attorney with 18+ years experience advocating for civic space protections and international legal compliance.', image_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80', order_index=1)
        TeamMember.objects.create(name='Dr. Rajesh Thapa', designation='Chairperson', category='executive', bio='Constitutional scholar and Senior Counsel leading strategic Supreme Court litigation and policy advocacy.', image_url='https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&q=80', order_index=2)
        TeamMember.objects.create(name='Bibek Adhikari', designation='Head of Rapid Response', category='executive', bio='Coordinates emergency relocation desks and 24/7 helpline operations across all 7 provinces.', image_url='https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&q=80', order_index=3)
        TeamMember.objects.create(name='Hon. Justice (Retd.) K. B. Gurung', designation='Senior Judicial Advisor', category='advisory', bio='Former Appellate Judge advising on constitutional rights, rule of law, and judicial accountability.', image_url='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80', order_index=1)
        TeamMember.objects.create(name='Prof. Rita Sharma', designation='Gender & Diversity Expert', category='advisory', bio='Senior academic leading gender policy audits and marginalized defender protection protocols.', image_url='https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&q=80', order_index=2)
        TeamMember.objects.create(name='Ramesh Chaudhary', designation='Koshi Field Coordinator', category='general', bio='Grassroots environmental defender monitoring river basin rights and forest advocacy in Eastern Nepal.', image_url='https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80', order_index=1)
        TeamMember.objects.create(name='Sabina Mahato', designation='Madhesh Paralegal Lead', category='general', bio='Community paralegal specializing in gender violence defense and local legal aid representation.', image_url='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80', order_index=2)

    if not Collaboration.objects.exists():
        Collaboration.objects.create(name='National Human Rights Commission (NHRC)', category='institutional', logo_url='https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=400&q=80', blurb='Formal memorandum of understanding for joint fact-finding missions and rapid defender alert escalation.', website_url='#', order_index=1)
        Collaboration.objects.create(name='International Rights Protection Coalition', category='institutional', logo_url='https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=400&q=80', blurb='Global alliance providing emergency diplomatic backing and international emergency grants for high-risk advocates.', website_url='#', order_index=2)
        Collaboration.objects.create(name='Nepal Pro-Bono Legal Alliance', category='institutional', logo_url='https://images.unsplash.com/photo-1450133064473-71024230f91b?w=400&q=80', blurb='Pro-bono network of 250+ legal practitioners extending emergency courtroom representation across all district courts.', website_url='#', order_index=3)
        Collaboration.objects.create(name='Adv. Govinda K.C.', category='individual', logo_url='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80', blurb='Senior Advocate offering emergency bail litigation and habeas corpus writs across Supreme and High Courts.', website_url='#', order_index=1)
        Collaboration.objects.create(name='Dr. Anita Bhattarai', category='individual', logo_url='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80', blurb='Digital security expert providing encrypted communication channels and digital forensics support for field monitors.', website_url='#', order_index=2)

    if not Video.objects.exists():
        Video.objects.create(title='Voices of Frontline Defenders in Nepal', embed_url='https://www.youtube.com/embed/5qap5aO4i9A', category='Documentary', published_date=date(2025, 6, 1))
        Video.objects.create(title='Provincial Helpdesk Operations & Protection Protocols', embed_url='https://www.youtube.com/embed/L_LUpnjgPso', category='Training', published_date=date(2025, 9, 15))


try:
    # Temporarily force migrations and bootstrap on Vercel cold start 
    _maybe_bootstrap()
except Exception as e:
    print(f"WSGI bootstrap info: {e}")

app = application
