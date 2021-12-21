from django_filters import rest_framework

from reviews.models import Title


class TitleFilter(rest_framework.FilterSet):
    genre = rest_framework.CharFilter(field_name='genre__slug', lookup_expr='icontains')
    category = rest_framework.CharFilter(field_name='category__slug', lookup_expr='icontains')
    name = rest_framework.CharFilter(field_name='name', lookup_expr='contains')
    year = rest_framework.NumberFilter(field_name='year', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ('year', 'name', 'genre', 'category')
