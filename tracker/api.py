from django.db.models import QuerySet
from django.utils.dateparse import parse_date
from rest_framework import filters, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from .models import Category, Food, FoodEvent, TeamMember
from .serializers import (
    CategorySerializer,
    FoodEventSerializer,
    FoodSerializer,
    TeamMemberSerializer,
)


class OpenModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]


class CategoryViewSet(OpenModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TeamMemberViewSet(OpenModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer


class FoodViewSet(OpenModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class FoodEventViewSet(OpenModelViewSet):
    queryset = FoodEvent.objects.select_related('food', 'consumer', 'category')
    serializer_class = FoodEventSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['food__name', 'consumer__name', 'category__name', 'notes']
    ordering_fields = ['consumed_at', 'created_at']
    ordering = ['-consumed_at']

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter_queryset(queryset)
        for parameter, field in (
            ('category', 'category_id'),
            ('consumer', 'consumer_id'),
            ('food', 'food_id'),
        ):
            value = self.request.query_params.get(parameter)
            if value is not None:
                try:
                    queryset = queryset.filter(**{field: int(value)})
                except ValueError as exc:
                    raise ValidationError(
                        {parameter: 'Enter a valid integer ID.'},
                    ) from exc

        for parameter, lookup in (
            ('from_date', 'consumed_at__date__gte'),
            ('to_date', 'consumed_at__date__lte'),
        ):
            value = self.request.query_params.get(parameter)
            if value is not None:
                parsed_date = parse_date(value)
                if parsed_date is None:
                    raise ValidationError(
                        {parameter: 'Enter a valid date in YYYY-MM-DD format.'},
                    )
                queryset = queryset.filter(**{lookup: parsed_date})

        start = self.request.query_params.get('from_date')
        end = self.request.query_params.get('to_date')
        if start is not None and end is not None:
            if parse_date(start) > parse_date(end):
                raise ValidationError(
                    {'to_date': 'The end date must be on or after the start date.'},
                )
        return queryset
