from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import  HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from xhtml2pdf import pisa
from .tasks import payment_completed
import io
import os
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError ,NotFound
from .models import Order, OrderItem, Cart , CartItem
from product.models import Product
from payment.models import Payment
from .serializers import(
    CreateOrderSerializer,
    OrderItemSerializer,
    CartSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    CartItemSerializer,
    OrderSerializer,
) 

# View for checking out a cart and creating an order
class CheckoutView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        if not Payment.objects.filter(order=order, is_paid=True).exists():
            return Response(
                {'error': 'Payment must be completed before checkout.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment_completed(order.id)
        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'total_price': order.total_price,
            'created': order.created,
        }, status=status.HTTP_201_CREATED)

# View for listing all order items of a user
class OrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
# View for listing all orders of a user
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        orders=Order.objects.filter(user=self.request.user)
        # if not orders:
        #     raise NotFound("You do not have any orders yet.")
        return orders

# View for retrieving a specific order
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    def get_object(self):
        return get_object_or_404(Order, id=self.kwargs["pk"], user=self.request.user)

# View for adding items to the cart
class AddCartItemView(generics.CreateAPIView):
    serializer_class = AddCartItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise ValidationError("User must be logged in to add items to the cart.")

        # Check if a cart exists for the user, create one if it doesn't
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data, context={"cart_id": cart.id})
        serializer.is_valid(raise_exception=True)
        cart_item = serializer.save()
        return Response({
            'message': 'Item added to cart successfully',
            'item_id': cart_item.id,
            'quantity': cart_item.quantity,
        }, status=status.HTTP_201_CREATED)

# View for updating items in the cart
class UpdateCartItemView(generics.UpdateAPIView):
    serializer_class = UpdateCartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_object(self):
        product_id = self.request.data.get("product_id") or self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=self.request.user)
        return get_object_or_404(CartItem, product=product, cart=cart)
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Item updated successfully",
                "data": response.data
            },
            status=status.HTTP_200_OK
        )

# View for deleting items from the cart
class DeleteCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_object(self):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=self.request.user)
        return get_object_or_404(CartItem, product=product, cart=cart)
    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# View for retrieving the current user's cart
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Cart.objects.filter(user=self.request.user).latest('created')

#invoice creation pdf
@staff_member_required
def admin_order_pdf(request,order_id):
    order=get_object_or_404(Order,id=order_id)
    html=render_to_string('orders/invoice.html',{'order':order})
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="order_{order_id}.pdf"' 
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=result)

    if pdf.err:
        return HttpResponse("Error rendering PDF", status=500)
    # Write PDF data to the HTTP response
    response.write(result.getvalue())
    return response