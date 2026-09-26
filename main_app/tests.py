import copy
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import django.template.context

# Python 3.14 copy.copy compatibility fix for Django template Context test recorder
def _safe_context_copy(self):
    req = getattr(self, 'request', None)
    if req is not None:
        duplicate = self.__class__(req)
    else:
        duplicate = django.template.context.Context()
    if hasattr(self, 'dicts'):
        duplicate.dicts = [d.copy() for d in self.dicts]
    return duplicate

django.template.context.BaseContext.__copy__ = _safe_context_copy
django.template.context.Context.__copy__ = _safe_context_copy

from main_app.models import (
    Stats, Province, News, Resource, Membership, Incident,
    PopupConfig, Gallery, Blog, Video, GatedDownloadLead,
    TeamMember, Collaboration, NewsFlash
)

class HRDForumTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test province
        self.province = Province.objects.create(
            name="Bagmati Province Desk (Central HQ)",
            code="p3",
            base_city="Kathmandu",
            coords_lat=27.7172,
            coords_lng=85.3240,
            coordinators_count=20,
            helpline_phone="+977-01-55511400",
            address="Thapagaun, New Baneshwor, Kathmandu",
            active_cases=35,
            description="HQ Desk",
            long_summary="Long summary for HQ"
        )
        
        # Create test stats
        self.stats = Stats.objects.create(
            provincial_networks=7,
            monitored_defenders=1200,
            resolved_cases=150,
            total_visitors=500
        )
        
        # Create test news
        self.news = News.objects.create(
            title="Test News Article",
            summary="Test news summary",
            content="Test news full content",
            category="Safety"
        )
        
        # Create test resource
        self.resource = Resource.objects.create(
            title="Test Protection Guide",
            category="Report",
            format="PDF",
            file_size="2.5 MB",
            file_url="https://example.com/guide.pdf",
            is_gated=True
        )
        
        # Create test superuser A
        self.superuser_a = User.objects.create_superuser(
            username='admin_a',
            email='admin_a@test.org',
            password='testpassword123'
        )

        # Create test staff user B
        self.staff_user_b = User.objects.create_user(
            username='staff_b',
            email='staff_b@test.org',
            password='testpassword123',
            is_staff=True
        )

        # Create test regular non-staff user C
        self.regular_user_c = User.objects.create_user(
            username='user_c',
            email='user_c@test.org',
            password='testpassword123',
            is_staff=False,
            is_superuser=False
        )

    def test_public_api_endpoints(self):
        """Verify all public read API endpoints return status 200 and valid JSON data."""
        endpoints = [
            '/api/stats/',
            '/api/stats',
            '/api/provinces/',
            '/api/provinces',
            f'/api/provinces/{self.province.id}/',
            '/api/news/',
            '/api/news',
            f'/api/news/{self.news.id}/',
            '/api/resources/',
            '/api/resources',
            '/api/popup/',
            '/api/popup',
            '/api/gallery/',
            '/api/blogs/',
            '/api/videos/',
            '/api/news-flashes/',
            '/api/team/',
            '/api/collaborations/'
        ]
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed GET for {url}")

        resources = self.client.get('/api/resources/').json()
        gated_resource = next(item for item in resources if item['id'] == self.resource.id)
        self.assertEqual(gated_resource['file_url'], '')

        collaboration = Collaboration.objects.create(
            name='Partner Organization',
            category='institutional',
            blurb='Partner details for the public card.',
            website_url='https://partner.example.org',
        )
        partners = self.client.get('/api/collaborations/').json()
        partner_data = next(item for item in partners if item['id'] == collaboration.id)
        self.assertEqual(partner_data['website_url'], 'https://partner.example.org')
        self.assertEqual(partner_data['category_label'], 'Institutional Collaboration')

    def test_resource_edit_saves_visible_fields_and_access_setting(self):
        from .forms import ResourceForm

        category_choices = dict(ResourceForm().fields['category'].choices)
        self.assertIn('Report', category_choices)
        self.assertIn('Publication', category_choices)
        self.assertIn('By-Laws', category_choices)
        self.assertIn('Other', category_choices)
        legacy_resource = Resource(title='Legacy document', category='Document')
        self.assertIn('Document', dict(ResourceForm(instance=legacy_resource).fields['category'].choices))

        self.client.force_login(self.staff_user_b)
        response = self.client.post(
            f'/portal/resources/{self.resource.id}/edit/',
            {
                'title': 'Updated protection guide',
                'category': 'Report',
                'format': 'PDF',
                'file_size': '1.3 MB',
                'file_url': 'https://example.com/updated-guide.pdf',
                'is_gated': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.title, 'Updated protection guide')
        self.assertEqual(self.resource.file_size, '1.3 MB')
        self.assertTrue(self.resource.is_gated)

    def test_form_submissions(self):
        """Verify public submission endpoints for membership, incident, and gated downloads."""
        # Membership submission
        mem_data = {
            "full_name": "Test Defender",
            "email": "defender@example.com",
            "phone": "9800000000",
            "province": "Bagmati Province",
            "organization": "Rights NGO",
            "role": "Monitor"
        }
        res_mem = self.client.post('/api/membership/', data=mem_data, content_type='application/json')
        self.assertEqual(res_mem.status_code, 201)
        self.assertTrue(Membership.objects.filter(email="defender@example.com").exists())

        # Incident report submission
        inc_data = {
            "reporter_name": "Alert Reporter",
            "contact_info": "9811111111",
            "province": "Bagmati Province",
            "incident_type": "Urgent Support",
            "details": "Urgent emergency situation in district.",
            "priority": "High"
        }
        res_inc = self.client.post('/api/incident/', data=inc_data, content_type='application/json')
        self.assertEqual(res_inc.status_code, 201)
        self.assertTrue(Incident.objects.filter(reporter_name="Alert Reporter").exists())

        # Gated download submission
        gated_data = {
            "user_name": "Lead User",
            "user_email": "lead@example.com",
            "resource_id": self.resource.id
        }
        res_gated = self.client.post('/api/resource/download-access/', data=gated_data, content_type='application/json')
        self.assertEqual(res_gated.status_code, 200)
        self.assertTrue(GatedDownloadLead.objects.filter(user_email="lead@example.com").exists())

    def test_legacy_admin_api_retired(self):
        """Legacy JSON admin API must return 410 Gone."""
        login_data = {
            "username": "admin_a",
            "password": "testpassword123"
        }
        res_login = self.client.post('/api/admin/login/', data=login_data, content_type='application/json')
        self.assertEqual(res_login.status_code, 410)

        headers = {'HTTP_AUTHORIZATION': 'Bearer unused-token'}
        res_incidents = self.client.get('/api/incidents/', **headers)
        self.assertEqual(res_incidents.status_code, 410)

        res_memberships = self.client.get('/api/memberships/', **headers)
        self.assertEqual(res_memberships.status_code, 410)

    def test_unauthenticated_and_non_staff_authorization_boundaries(self):
        """Verify unauthenticated and standard non-staff users cannot access portal routes or admin APIs."""
        # Unauthenticated redirect to login
        res_unauth = self.client.get('/portal/')
        self.assertEqual(res_unauth.status_code, 302)

        # Legacy admin API is retired (410), not open
        res_api_unauth = self.client.get('/api/incidents/')
        self.assertEqual(res_api_unauth.status_code, 410)

        # Non-staff user C logged in
        self.client.force_login(self.regular_user_c)

        # Non-staff redirected from portal routes
        res_non_staff_portal = self.client.get('/portal/')
        self.assertEqual(res_non_staff_portal.status_code, 302)

        # Non-staff also gets 410 on retired API
        res_non_staff_api = self.client.get('/api/incidents/')
        self.assertEqual(res_non_staff_api.status_code, 410)

    def test_portal_login_blocks_open_redirect(self):
        """Portal login must not redirect to an external next= URL."""
        res = self.client.post(
            '/portal/login/?next=https://evil.example/phish',
            {'username': 'admin_a', 'password': 'testpassword123'},
        )
        self.assertEqual(res.status_code, 302)
        self.assertNotIn('evil.example', res['Location'])
        self.assertTrue(
            res['Location'].endswith('/portal/') or '/portal/' in res['Location']
        )

    def test_exposed_legacy_admin_password_is_rejected(self):
        self.superuser_a.set_password('Hrdforun@11')
        self.superuser_a.save(update_fields=['password'])
        for login_url in ['/portal/login/', '/admin/login/']:
            response = self.client.post(
                login_url,
                {'username': self.superuser_a.username, 'password': 'Hrdforun@11'},
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('_auth_user_id', self.client.session)

    def test_membership_decisions_require_post(self):
        membership = Membership.objects.create(
            full_name='Pending Defender',
            email='pending@example.org',
            province=self.province,
        )
        self.client.force_login(self.staff_user_b)
        response = self.client.get(f'/portal/memberships/{membership.id}/approve/')
        self.assertEqual(response.status_code, 405)
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'pending')

    def test_staff_vs_superuser_vertical_authorization(self):
        """Verify staff User B can access operational portal views but is denied access to user/group admin views."""
        # Authenticate staff User B (non-superuser)
        self.client.force_login(self.staff_user_b)

        # Staff can access operational pages
        operational_urls = [
            '/portal/',
            '/portal/incidents/',
            '/portal/memberships/',
            '/portal/news/',
            '/portal/gallery/',
            '/portal/resources/',
            '/portal/videos/',
            '/portal/news-flashes/',
            '/portal/popups/',
            '/portal/provinces/',
            '/portal/team/',
            '/portal/collaborations/',
            '/portal/gated-leads/'
        ]
        for url in operational_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Staff access failed for {url}")

        # Staff User B cannot access superuser-only user/group management views
        superuser_urls = [
            '/portal/users/',
            '/portal/users/add/',
            f'/portal/users/{self.superuser_a.id}/edit/',
            f'/portal/users/{self.superuser_a.id}/delete/',
            '/portal/groups/',
            '/portal/groups/add/'
        ]
        for url in superuser_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302, f"Staff user B should be redirected for superuser route {url}")

    def test_superuser_full_authorization(self):
        """Verify Superuser A has full access to all operational and user management portal pages."""
        self.client.force_login(self.superuser_a)

        all_portal_urls = [
            '/portal/',
            '/portal/incidents/',
            '/portal/memberships/',
            '/portal/news/',
            '/portal/gallery/',
            '/portal/resources/',
            '/portal/videos/',
            '/portal/news-flashes/',
            '/portal/popups/',
            '/portal/provinces/',
            '/portal/team/',
            '/portal/collaborations/',
            '/portal/gated-leads/',
            '/portal/users/',
            '/portal/groups/'
        ]
        for url in all_portal_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Superuser GET failed for {url}")

    def test_sqli_and_xss_input_resilience(self):
        """Verify that search filters and public form endpoints safely handle SQLi and XSS payloads without raising unhandled errors or reflecting raw scripts."""
        sqli_payload = "' OR '1'='1' --"
        xss_payload = "<script>alert('xss')</script>"

        # 1. Search filter with SQLi / XSS
        search_urls = [
            f'/portal/news/?q={sqli_payload}',
            f'/portal/news/?q={xss_payload}',
            f'/portal/incidents/?q={sqli_payload}',
            f'/portal/incidents/?q={xss_payload}',
        ]
        self.client.force_login(self.superuser_a)
        for url in search_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn("<script>alert('xss')</script>", res.content.decode('utf-8'))

        # 2. Form submission with XSS & SQLi payloads
        mem_payload = {
            "full_name": xss_payload,
            "email": "xss_test@example.com",
            "phone": "9800000000",
            "province": "Bagmati Province",
            "organization": sqli_payload,
            "role": "Monitor"
        }
        res_mem = self.client.post('/api/membership/', data=mem_payload, content_type='application/json')
        self.assertEqual(res_mem.status_code, 201)

        # Confirm data is stored verbatim via ORM parameterization without executing SQLi
        mem_obj = Membership.objects.get(email="xss_test@example.com")
        self.assertEqual(mem_obj.full_name, xss_payload)
        self.assertEqual(mem_obj.organization, sqli_payload)
