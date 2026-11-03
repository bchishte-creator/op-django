from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import FoodEventForm, FoodEventSearchForm
from .models import FoodEvent


def home(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    top_category = (
        FoodEvent.objects.values('category__name')
        .annotate(event_count=Count('pk'))
        .order_by('-event_count', 'category__name')
        .first()
    )
    context = {
        'meal_count': FoodEvent.objects.count(),
        'week_count': FoodEvent.objects.filter(consumed_at__date__gte=week_start).count(),
        'top_category': top_category['category__name'] if top_category else '—',
        'recent_events': FoodEvent.objects.select_related(
            'food',
            'consumer',
            'category',
        )[:5],
    }
    return render(request, 'tracker/home.html', context)


def submit(request):
    if request.method == 'POST':
        form = FoodEventForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, 'Food event saved.')
            return redirect('tracker:submit')
    else:
        form = FoodEventForm()
    return render(request, 'tracker/submit.html', {'form': form})


def search(request):
    form = FoodEventSearchForm(request.GET or None)
    events = FoodEvent.objects.select_related('food', 'consumer', 'category')

    if form.is_bound and form.is_valid():
        query = form.cleaned_data['q']
        category = form.cleaned_data['category']
        period = form.cleaned_data['period']

        if query:
            events = events.filter(
                Q(food__name__icontains=query)
                | Q(consumer__name__icontains=query)
                | Q(category__name__icontains=query)
                | Q(notes__icontains=query)
            )
        if category:
            events = events.filter(category=category)

        today = timezone.localdate()
        if period == 'today':
            events = events.filter(consumed_at__date=today)
        elif period == 'week':
            week_start = today - timedelta(days=today.weekday())
            events = events.filter(consumed_at__date__gte=week_start)
        elif period == 'month':
            events = events.filter(
                consumed_at__year=today.year,
                consumed_at__month=today.month,
            )
    elif form.is_bound:
        events = events.none()

    return render(
        request,
        'tracker/search.html',
        {'form': form, 'events': events, 'result_count': events.count()},
    )


def gallery(request):
    events = (
        FoodEvent.objects.select_related('food', 'consumer', 'category')
        .exclude(photo='')
    )
    return render(request, 'tracker/gallery.html', {'events': events})


def about(request):
    return render(request, 'tracker/about.html')
