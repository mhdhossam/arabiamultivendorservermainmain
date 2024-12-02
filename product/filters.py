from django.db.models import Q, OuterRef, Subquery

from django_filters import BooleanFilter, CharFilter, FilterSet

from .models import Product

from django.contrib.postgres.search import TrigramSimilarity

class CustomBooleanFilter(BooleanFilter):
    def filter(self, qs, value):
        if value is False:
            return qs

        return super().filter(qs, value)


class ProductFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")
    on_sale = CustomBooleanFilter(field_name="sale_price", lookup_expr="gt")
    category = CharFilter(field_name="category__parent__slug", lookup_expr="icontains")
    sub_category = CharFilter(field_name="category__slug", lookup_expr="icontains")
    brand = CharFilter(field_name="brand__name", lookup_expr="icontains")
    supplier = CharFilter(field_name="supplier__id", lookup_expr="iexact")
    search = CharFilter(method='filter_by_search')
    class Meta:
        model = Product
        fields = [
            "name",
            "on_sale",
            "brand",
            "category",
            "sub_category",
            "search",
        ]
    def filter_by_search(self, queryset, name, value):
        if value:
            return queryset.annotate(
                similarity=TrigramSimilarity('translations__name', value)
            ).filter(
                Q(translations__language_code__in=['en', 'ar']) &
                Q(similarity__gt=0.1)
            ).order_by('-similarity')
        return queryset
    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        price_value_min = self.request.query_params.get("price_value_min")
        price_value_max = self.request.query_params.get("price_value_max")

        if price_value_min and price_value_max:
            queryset = queryset.filter(
                Q(price__range=(price_value_min, price_value_max))
                | Q(sale_price__range=(price_value_min, price_value_max))
                | Q(
                    price=0,
                    sale_price=0,
                    price_range_min__gte=price_value_min,
                    price_range_max__lte=price_value_max,
                )
            ).distinct()

        return queryset
