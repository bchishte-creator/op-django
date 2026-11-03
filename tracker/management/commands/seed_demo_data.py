from datetime import datetime, time, timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import Category, Food, FoodEvent, TeamMember


class Command(BaseCommand):
    help = 'Create sample people, categories, foods, and events for the UI.'

    def handle(self, *args, **options):
        examples = [
            ('Greek yogurt', 'Patrick', 'Dairy', 0, time(12, 20), 'greek-yogurt.jpg'),
            ('Veggie bowl', 'Maya', 'Lunch', 0, time(12, 5), 'veggie-bowl.jpg'),
            ('Tacos', 'Jordan', 'Dinner', 1, time(18, 30), 'tacos.jpg'),
            ('Pasta', 'Amira', 'Dinner', 2, time(19, 0), 'pasta.jpg'),
            ('Fruit cup', 'Patrick', 'Snack', 3, time(15, 15), 'fruit-cup.jpg'),
            ('Sandwich', 'Maya', 'Lunch', 4, time(12, 0), 'sandwich.jpg'),
            ('Chicken salad', 'Amira', 'Lunch', 5, time(12, 30), 'chicken-salad.jpg'),
            ('Blueberry muffin', 'Jordan', 'Breakfast', 6, time(9, 0), 'blueberry-muffins.jpg'),
            ('Veggie burrito', 'Maya', 'Lunch', 1, time(13, 5), 'veggie-burrito.jpg'),
            ('Apple and almonds', 'Patrick', 'Snack', 2, time(15, 15), 'apple-almonds.jpg'),
        ]
        today = timezone.localdate()
        current_timezone = timezone.get_current_timezone()

        for food_name, person_name, category_name, days_ago, event_time, photo_name in examples:
            food, _ = Food.objects.get_or_create(name=food_name)
            person, _ = TeamMember.objects.get_or_create(name=person_name)
            category, _ = Category.objects.get_or_create(name=category_name)
            consumed_at = timezone.make_aware(
                datetime.combine(today - timedelta(days=days_ago), event_time),
                current_timezone,
            )
            event, _ = FoodEvent.objects.get_or_create(
                food=food,
                consumer=person,
                category=category,
                consumed_at=consumed_at,
            )
            image_path = (
                Path(settings.BASE_DIR)
                / 'tracker'
                / 'static'
                / 'tracker'
                / 'images'
                / photo_name
            )
            if not event.photo and image_path.is_file():
                with image_path.open('rb') as image:
                    event.photo.save(image_path.name, File(image), save=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'Demo data ready: {FoodEvent.objects.count()} food events.'
            )
        )
