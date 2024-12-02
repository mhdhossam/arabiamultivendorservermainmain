from rest_framework import serializers
from django.db import transaction
from .models import *
from product.serializers import ProductSerializer,ProductMinimalSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product= ProductMinimalSerializer(many=False)
    sub_total=serializers.SerializerMethodField()
    class Meta:
        model= CartItem
        fields = ['id','cart','product','quantity','sub_total']
    def get_sub_total(self,cartitem):
        return cartitem.quantity*cartitem.product.price_after_discount


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()
    
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("There is no product associated with the given ID")
        return value
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        product_id = self.initial_data.get("product_id")
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("The product with the given ID does not exist.")
    
        if value > product.stock_quantity:
            raise serializers.ValidationError(f"Cannot add more than {product.stock_quantity} of this product to the cart.")
        return value

    
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        # Fetch the current cart to check if it's checked out
        cart = Cart.objects.get(id=cart_id)
        
        # If the cart is checked out, create a new cart
        if cart.checked_out:
            cart = Cart.objects.create(user=cart.user) 
        quantity = self.validated_data["quantity"] 
        
        try:
            cartitem = CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cartitem.quantity += quantity
            cartitem.save()
            
            self.instance = cartitem
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")

        return self.instance


    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=["quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]
        
    def get_total_price(self, cart):
        return sum(item.quantity * item.product.price_after_discount for item in cart.items.all())
    def validate(self, data):
        # Check if attempting to mark the cart as checked out
        if data.get('checked_out', False):
            cart = self.instance
            if not Payment.objects.filter(order__cart=cart, is_paid=True).exists():
                raise serializers.ValidationError("Payment must be completed before checkout.")
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    product=ProductSerializer()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity","color","size","total_price"]
    def get_total_price(self, order_item):
        return order_item.get_final_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items=OrderItemSerializer(many=True , read_only=True)
    total_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    class Meta:
        model = Order
        fields = ["id","is_paid","created","user","payment_method","shipping_status","total_price","order_items"]



class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This cart_id is invalid")
        elif not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Sorry your cart is empty")
        
        return cart_id
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]

            # Create the order
            order = Order.objects.create(user_id=user_id)
            cartitems = CartItem.objects.filter(cart_id=cart_id)
            orderitems = []
            total_order_price = 0  
            for item in cartitems:
                item_total_price = item.quantity * item.product.price_after_discount
                order_item = OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item_total_price,
                )
                orderitems.append(order_item)
                total_order_price += item_total_price
                product = item.product
                if item.quantity > product.stock_quantity:
                    raise ValidationError(f"Insufficient stock for {product.name}.")
                product.stock_quantity -= item.quantity
                product.total_sold += item.quantity
                product.save()
            # Bulk create all order items
            OrderItem.objects.bulk_create(orderitems)
            order.total_price = total_order_price  
            order.save()

            # Mark the cart as checked out
            cart = Cart.objects.get(id=cart_id)
            cart.checked_out = True
            cart.save()

            return order
