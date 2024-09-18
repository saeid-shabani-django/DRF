from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Product, Category, Comment, Cart, CartItem
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer, CartSerializer, CartItemSerializer
from rest_framework import status, mixins
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from . import pagination

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter,SearchFilter]
    filterset_fields = ['category_id','inventory']
    ordering_fields = ['name','unit_price']
    search_fields = ['name']
    pagination_class = pagination.CustomPagination
    queryset = Product.objects.select_related('category').all()




    def get_serializer_context(self):
        return {'request':self.request}

    def destroy(self,request,pk):
        product = get_object_or_404(Product.objects.select_related('category').all(), pk=pk)
        if product.order_items.count() > 0:
            return Response({
                                'error': 'Cannot delete some instances of model  because they are referenced through protected foreign key'})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





class CategoryViewSet(ModelViewSet):

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def destroy(self,request,pk):
        category = get_object_or_404(Category.objects.all(), pk=pk)
        if category.products.count() > 0:
            return Response({
                                'error': 'Cannot delete some instances of model  because they are referenced through protected foreign key'})
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return Comment.objects.filter(product_id = product_pk).all()

    def get_serializer_context(self):
        return {'product_pk':self.kwargs['product_pk']}


class CartViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product').all()

class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.select_related('product').filter(cart_id = cart_pk)