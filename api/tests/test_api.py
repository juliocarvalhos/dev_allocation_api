"""End-to-end tests through HTTP: authentication, CRUD and rule errors."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Allocation

from .factories import make_developer, make_project, make_technology


class AuthenticationTests(APITestCase):
    endpoints = [
        '/api/technologies/',
        '/api/developers/',
        '/api/projects/',
        '/api/allocations/',
    ]

    def test_endpoints_require_authentication(self):
        for url in self.endpoints:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_flow_grants_access(self):
        get_user_model().objects.create_user(username='manager', password='s3cret-pass')

        response = self.client.post(
            '/api/token/', {'username': 'manager', 'password': 's3cret-pass'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(self.client.get('/api/projects/').status_code, status.HTTP_200_OK)

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post('/api/token/', {'username': 'nobody', 'password': 'x'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_docs_are_public(self):
        self.assertEqual(self.client.get('/api/schema/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/docs/').status_code, status.HTTP_200_OK)


class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='manager', password='s3cret-pass')
        self.client.force_authenticate(user)


class CrudTests(AuthenticatedAPITestCase):
    def test_full_allocation_workflow(self):
        tech = self.client.post('/api/technologies/', {'name': 'Python'})
        self.assertEqual(tech.status_code, status.HTTP_201_CREATED)
        tech_id = tech.data['id']

        dev = self.client.post(
            '/api/developers/', {'name': 'Ada', 'technologies': [tech_id]}, format='json'
        )
        self.assertEqual(dev.status_code, status.HTTP_201_CREATED)

        project = make_project('Backend')
        response = self.client.patch(
            f'/api/projects/{project.id}/', {'technologies': [tech_id]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['planned_hours'], 88)

        allocation = self.client.post(
            '/api/allocations/',
            {
                'project': project.id,
                'developer': dev.data['id'],
                'hours': 40,
            },
        )
        self.assertEqual(allocation.status_code, status.HTTP_201_CREATED)

        listing = self.client.get('/api/allocations/')
        self.assertEqual(listing.data['count'], 1)

        deleted = self.client.delete(f"/api/allocations/{allocation.data['id']}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Allocation.objects.exists())

    def test_create_project_computes_planned_hours(self):
        tech = make_technology('Python')
        response = self.client.post(
            '/api/projects/',
            {
                'name': 'Short',
                'start_date': '2025-03-03',
                'end_date': '2025-03-07',
                'technologies': [tech.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['planned_hours'], 40)

    def test_duplicate_technology_name_is_rejected(self):
        make_technology('Python')
        response = self.client.post('/api/technologies/', {'name': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AllocationRuleErrorsOverHTTPTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        python = make_technology('Python')
        self.project = make_project('Backend', technologies=[python])
        self.developer = make_developer('Ada', technologies=[python])

    def post(self, hours):
        return self.client.post(
            '/api/allocations/',
            {
                'project': self.project.id,
                'developer': self.developer.id,
                'hours': hours,
            },
        )

    def test_rule_violation_returns_400_and_does_not_persist(self):
        response = self.post(hours=500)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertFalse(Allocation.objects.exists())

    def test_patch_cannot_bypass_hours_limit(self):
        allocation_id = self.post(hours=40).data['id']
        response = self.client.patch(f'/api/allocations/{allocation_id}/', {'hours': 500})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Allocation.objects.get().hours, 40)
