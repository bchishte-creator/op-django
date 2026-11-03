from io import BytesIO
from tempfile import TemporaryDirectory
from datetime import datetime, time, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from PIL import Image
from rest_framework.test import APITestCase

from .models import Category, Food, FoodEvent, TeamMember


class PageNavigationTests(TestCase):
    def test_all_mockup_pages_are_reachable(self):
        pages = (
            ('home', 'tracker/home.html', 'Welcome back, food trackers!'),
            ('submit', 'tracker/submit.html', 'Log a food event'),
            ('search', 'tracker/search.html', 'Search food events'),
            ('gallery', 'tracker/gallery.html', 'Food pictures'),
            ('about', 'tracker/about.html', 'About the tracker'),
            ('login', 'tracker/login.html', 'Sign in with the username and password you created.'),
        )

        for page_name, template_name, heading in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(f'tracker:{page_name}'))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template_name)
                self.assertContains(response, heading)
                for linked_page, _, _ in pages:
                    self.assertContains(response, reverse(f'tracker:{linked_page}'))


class LoginTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='food-tracker-user',
            email='food-tracker@example.com',
            password='test-password-123',
        )

    def test_login_page_authenticates_with_username(self):
        response = self.client.post(
            reverse('tracker:login'),
            {'username': self.user.username, 'password': 'test-password-123'},
        )

        self.assertRedirects(response, reverse('tracker:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_page_shows_error_for_invalid_credentials(self):
        response = self.client.post(
            reverse('tracker:login'),
            {'username': self.user.username, 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_authenticated_user_can_log_out(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('tracker:logout'))

        self.assertRedirects(response, reverse('tracker:login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class FoodEventPageTests(TestCase):
    def setUp(self):
        self.member = TeamMember.objects.create(name='Taylor')
        self.category = Category.objects.create(name='Lunch')

    def create_event(self, food_name, consumed_at=None):
        food = Food.objects.create(name=food_name)
        return FoodEvent.objects.create(
            food=food,
            consumer=self.member,
            category=self.category,
            consumed_at=consumed_at or timezone.now(),
        )

    def test_submit_page_saves_food_event(self):
        response = self.client.post(
            reverse('tracker:submit'),
            {
                'food_name': '  Tomato   sandwich ',
                'consumer': self.member.pk,
                'category': self.category.pk,
                'consumed_on': timezone.localdate().isoformat(),
                'consumed_time': '12:30',
                'notes': 'Fresh tomatoes',
            },
        )

        self.assertRedirects(response, reverse('tracker:submit'))
        self.assertEqual(FoodEvent.objects.count(), 1)
        event = FoodEvent.objects.select_related('food').get()
        self.assertEqual(event.food.name, 'Tomato sandwich')
        self.assertEqual(event.notes, 'Fresh tomatoes')

    def test_submit_page_saves_uploaded_photo(self):
        image_bytes = BytesIO()
        Image.new('RGB', (2, 2), color='green').save(image_bytes, format='PNG')
        photo = SimpleUploadedFile(
            'lunch.png',
            image_bytes.getvalue(),
            content_type='image/png',
        )

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse('tracker:submit'),
                    {
                        'food_name': 'Garden salad',
                        'consumer': self.member.pk,
                        'category': self.category.pk,
                        'consumed_on': timezone.localdate().isoformat(),
                        'consumed_time': '12:30',
                        'photo': photo,
                    },
                )

                self.assertRedirects(response, reverse('tracker:submit'))
                event = FoodEvent.objects.get()
                self.assertTrue(event.photo.name.endswith('lunch.png'))
                self.assertTrue(event.photo.storage.exists(event.photo.name))

    def test_search_filters_by_keyword_and_category(self):
        matching = self.create_event('Spinach salad')
        self.create_event('Pasta')

        response = self.client.get(
            reverse('tracker:search'),
            {'q': 'spinach', 'category': self.category.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['events']), [matching])
        self.assertContains(response, 'Spinach salad')
        self.assertNotContains(response, '>Pasta<')

    def test_gallery_only_shows_events_with_photos(self):
        event_with_photo = self.create_event('Photo meal')
        event_without_photo = self.create_event('No photo meal')
        event_with_photo.photo = 'food-events/sample.jpg'
        event_with_photo.save()

        response = self.client.get(reverse('tracker:gallery'))

        self.assertEqual(list(response.context['events']), [event_with_photo])
        self.assertNotIn(event_without_photo, response.context['events'])

    def test_homepage_statistics_come_from_saved_events(self):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        first_moment_of_week = timezone.make_aware(
            datetime.combine(week_start, time.min),
            timezone.get_current_timezone(),
        )
        self.create_event('One food')
        self.create_event(
            'Another food',
            first_moment_of_week - timedelta(seconds=1),
        )

        response = self.client.get(reverse('tracker:home'))

        self.assertEqual(response.context['meal_count'], 2)
        self.assertEqual(response.context['week_count'], 1)
        self.assertEqual(response.context['top_category'], 'Lunch')


class FoodTrackerAPITests(APITestCase):
    def setUp(self):
        self.food = Food.objects.create(name='Greek yogurt')
        self.member = TeamMember.objects.create(name='Patrick')
        self.category = Category.objects.create(name='Dairy')
        self.event = FoodEvent.objects.create(
            food=self.food,
            consumer=self.member,
            category=self.category,
            consumed_at=timezone.now(),
            notes='Plain yogurt',
        )

    def test_event_api_lists_records_and_searches(self):
        response = self.client.get(
            reverse('food-event-list'),
            {'search': 'Greek'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['food_name'], 'Greek yogurt')
        self.assertEqual(response.data['results'][0]['consumer_name'], 'Patrick')

    def test_event_api_creates_updates_and_deletes_records(self):
        payload = {
            'food': self.food.pk,
            'consumer': self.member.pk,
            'category': self.category.pk,
            'consumed_at': timezone.now().isoformat(),
            'notes': 'Team snack',
        }
        create_response = self.client.post(
            reverse('food-event-list'),
            payload,
            format='json',
        )

        self.assertEqual(create_response.status_code, 201)
        event_url = reverse('food-event-detail', args=[create_response.data['id']])

        put_response = self.client.put(
            event_url,
            {
                **payload,
                'notes': 'Replaced snack',
            },
            format='json',
        )
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.data['notes'], 'Replaced snack')

        patch_response = self.client.patch(
            event_url,
            {'notes': 'Updated snack'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data['notes'], 'Updated snack')

        delete_response = self.client.delete(event_url)
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(
            FoodEvent.objects.filter(pk=create_response.data['id']).exists()
        )

    def test_event_api_rejects_malformed_date_filters(self):
        response = self.client.get(
            reverse('food-event-list'),
            {'from_date': 'yesterday'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('from_date', response.data)
