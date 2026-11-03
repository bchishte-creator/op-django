from django.contrib import admin

from .models import Category, Food, FoodEvent, TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(FoodEvent)
class FoodEventAdmin(admin.ModelAdmin):
    list_display = ['food', 'consumer', 'category', 'consumed_at']
    list_filter = ['category', 'consumer', 'consumed_at']
    search_fields = ['food__name', 'consumer__name', 'category__name', 'notes']
    date_hierarchy = 'consumed_at'
