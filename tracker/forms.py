from datetime import datetime

from django import forms
from django.utils import timezone

from .models import Category, Food, FoodEvent


class FoodEventForm(forms.ModelForm):
    food_name = forms.CharField(
        label='Food name',
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Greek yogurt'}),
    )
    consumed_on = forms.DateField(
        label='Date consumed',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    consumed_time = forms.TimeField(
        label='Time',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )

    class Meta:
        model = FoodEvent
        fields = ['consumer', 'category', 'notes', 'photo']
        widgets = {
            'consumer': forms.Select(),
            'category': forms.Select(),
            'notes': forms.TextInput(
                attrs={'placeholder': 'Add optional details or ingredients'},
            ),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['consumer'].empty_label = 'Select a team member'
        self.fields['category'].empty_label = 'Select a category'
        self.fields['consumed_on'].initial = timezone.localdate()
        self.fields['consumed_time'].initial = timezone.localtime().time().replace(
            second=0,
            microsecond=0,
        )

    def clean_food_name(self):
        return ' '.join(self.cleaned_data['food_name'].split())

    def save(self, commit=True):
        event = super().save(commit=False)
        event.food, _ = Food.objects.get_or_create(name=self.cleaned_data['food_name'])
        event.consumed_at = timezone.make_aware(
            datetime.combine(
                self.cleaned_data['consumed_on'],
                self.cleaned_data['consumed_time'],
            ),
            timezone.get_current_timezone(),
        )
        if commit:
            event.save()
        return event


class FoodEventSearchForm(forms.Form):
    PERIOD_CHOICES = [
        ('', 'Any time'),
        ('today', 'Today'),
        ('week', 'This week'),
        ('month', 'This month'),
    ]

    q = forms.CharField(
        required=False,
        label='Keywords',
        widget=forms.SearchInput(attrs={'placeholder': 'Search food names or people'}),
    )
    category = forms.ModelChoiceField(
        required=False,
        label='Category',
        queryset=Category.objects.none(),
        empty_label='All categories',
    )
    period = forms.ChoiceField(
        required=False,
        label='Date range',
        choices=PERIOD_CHOICES,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
