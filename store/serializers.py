import math
from decimal import Decimal

from django.utils.text import slugify
from rest_framework import serializers
from .models import Product, Category, Comment, Cart, CartItem


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField(max_length=500)
    num_of_products = serializers.IntegerField(source='products.count',read_only=True)
    class Meta:
        model = Category
        fields = ['title','description']

    # def get_num_of_products(self,category):
    #     return category.products.count()



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','price','inventory','category','description']
    title = serializers.CharField(max_length=200,source='name')
    price = serializers.CharField(max_length=200,source='unit_price')
    # id = serializers.IntegerField()
    # name = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6,decimal_places=2)
    # inventory = serializers.IntegerField()
    # price_after_tax = serializers.SerializerMethodField()
    # category = serializers.HyperlinkedRelatedField(
    #     queryset= Category.objects.all(),
    #     view_name= 'category_detail',
    # )

    def get_price_after_tax(self,product:Product):
        return round(product.unit_price * Decimal(1.09),2)



    # def validate(self, data):
    #     print(type(data['unit_price']))
    #     if len(data['name']) < 10:
    #         raise serializers.ValidationError('the name Must be at least 10 charachters')
    #     if float(data['unit_price']) > float(25):
    #         raise serializers.ValidationError('not accepted')
    #     return data


    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product





class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id','name','body','status']

    def create(self, validated_data):
        product_pk = self.context['product_pk']
        return Comment.objects.create(product_id= product_pk,**validated_data)


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =['name','unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer()
    item_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id','product','quantity','item_price',]
    def get_item_price(self,cartitem):
        return cartitem.quantity * cartitem.product.unit_price






class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()


    class Meta:
        model = Cart
        fields = ['id','created_at','items','total_price']
        read_only_fields = ['id',]

    def get_total_price(self, cart):
        total = 0
        for c in cart.items.all():
            total += (c.product.unit_price * c.quantity)
        return total

