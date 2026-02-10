from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from apps.recruiter_app.models import Job
from apps.user_app.views.user_jobs import UserJobListView
import json

User = get_user_model()

class JobFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.recruiter = User.objects.create_user(username='recruiter', email='recruiter@example.com', password='password', is_recruiter=True)
        
        # Create sample jobs
        Job.objects.create(
            recruiter=self.recruiter,
            title='Software Engineer',
            description='React and Node developer',
            location='Remote',
            job_type='REMOTE',
            skills=['React', 'Node'],
            experience=2,
            work_time='full-time',
            status='OPEN'
        )
        Job.objects.create(
            recruiter=self.recruiter,
            title='Backend Developer',
            description='Python and Django developer',
            location='Bangalore',
            job_type='ONSITE',
            skills=['Python', 'Django'],
            experience=3,
            work_time='full-time',
            status='OPEN'
        )
        Job.objects.create(
            recruiter=self.recruiter,
            title='Frontend Intern',
            description='Learning React',
            location='Remote',
            job_type='REMOTE',
            skills=['React', 'Javascript'],
            experience=0,
            work_time='internship',
            status='OPEN'
        )
        Job.objects.create(
            recruiter=self.recruiter,
            title='Closed Job',
            description='Not visible',
            location='Noida',
            job_type='HYBRID',
            skills=['C++'],
            experience=5,
            work_time='contract',
            status='CLOSED'
        )

    def test_search_filter(self):
        view = UserJobListView.as_view()
        request = self.factory.get('/api/user/jobs/', {'search': 'Software'})
        response = view(request)
        self.assertEqual(len(response.data['data']['jobs']), 1)
        self.assertEqual(response.data['data']['jobs'][0]['title'], 'Software Engineer')

    def test_workmode_filter(self):
        view = UserJobListView.as_view()
        request = self.factory.get('/api/user/jobs/', {'workmode': 'remote'})
        response = view(request)
        self.assertEqual(len(response.data['data']['jobs']), 2)

    def test_worktime_filter(self):
        view = UserJobListView.as_view()
        request = self.factory.get('/api/user/jobs/', {'worktime': 'internship'})
        response = view(request)
        self.assertEqual(len(response.data['data']['jobs']), 1)
        self.assertEqual(response.data['data']['jobs'][0]['title'], 'Frontend Intern')

    def test_location_filter(self):
        view = UserJobListView.as_view()
        request = self.factory.get('/api/user/jobs/', {'location': 'Bangalore'})
        response = view(request)
        self.assertEqual(len(response.data['data']['jobs']), 1)
        self.assertEqual(response.data['data']['jobs'][0]['location'], 'Bangalore')

    def test_skills_filter(self):
        view = UserJobListView.as_view()
        # Single skill
        request = self.factory.get('/api/user/jobs/', {'skills': 'Python'})
        response = view(request)
        self.assertEqual(len(response.data['data']['jobs']), 1)
        
        # Multiple skills (AND logic)
        request = self.factory.get('/api/user/jobs/', {'skills': 'React,Javascript'})
        response = view(request)
        self.assertEqual(len(response.data['data']['jobs']), 1)
        self.assertEqual(response.data['data']['jobs'][0]['title'], 'Frontend Intern')

    def test_combined_filters(self):
        view = UserJobListView.as_view()
        request = self.factory.get('/api/user/jobs/', {'workmode': 'remote', 'skills': 'React'})
        response = view(request)
        # Software Engineer and Frontend Intern both match
        self.assertEqual(len(response.data['data']['jobs']), 2)
