from rest_framework import serializers
from .models import Service, Subcategory, PromoCode, Category # Импортируй свои модели
    

class PromoCodeSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    class Meta:
        model = PromoCode
        fields = ['percent', 'is_active']
    
    def get_is_active(self, obj):
        return obj.is_active()
    
    def get_percent(self, obj):
        return obj.discount_percent


class CategorySerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    sub_cat_name = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['cat_name', 'icon', 'sub_cat_name']
        
    def get_icon(self, obj):
        return obj.get_img_display()

    def get_sub_cat_name(self, obj):
        return obj.sub_cat.all()[0].name


class ServiceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = ['name', 'price', 'service_id', 'min_count', 'max_count', 'speed', 'quality', 'text_info', 'text_pre_info', 'link_p']
        
    def get_price(self, obj):
        return obj.price_per_one()
    
    
class ServiceInfoSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Service
        fields = ['name', 'slug', 'price', 'service_id', 'min_count', 'max_count', 'speed_day', 'speed', 'quality', 'text_info', 'text_pre_info', 'category']
    

class SubcategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)  # Связанные сервисы
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = ['name', 'slug', 'icon', 'services']
        
    def get_icon(self, obj):
        return obj.get_img_display()


class SubcategorySlugSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    
    class Meta:
        model = Subcategory
        fields = ['name', 'slug', 'icon']
        
    def get_icon(self, obj):
        return obj.get_img_display()