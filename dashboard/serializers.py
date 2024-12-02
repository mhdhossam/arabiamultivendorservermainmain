from rest_framework import serializers

class VendorOrderSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_products_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    weekly_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
