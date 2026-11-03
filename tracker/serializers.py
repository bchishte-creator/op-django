from rest_framework import serializers

from .models import Category, Food, FoodEvent, TeamMember


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name']


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', 'name']


class FoodEventSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    consumer_name = serializers.CharField(source='consumer.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FoodEvent
        fields = [
            'id',
            'food',
            'food_name',
            'consumer',
            'consumer_name',
            'category',
            'category_name',
            'consumed_at',
            'notes',
            'photo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
