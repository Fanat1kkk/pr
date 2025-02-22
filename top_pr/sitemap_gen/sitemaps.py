from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from my_site.models import Service, Category, Subcategory


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.all()
    
    def location(self, obj):
        return f'{obj.get_absolute_url()}'
    
    
class SocialsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Category.objects.all()
    
    def location(self, obj):
        return f'{obj.get_absolute_url()}'
    
    
# class SubcategoriesSitemap(Sitemap):
#     changefreq = "monthly"
#     priority = 0.6  # Можно сделать ниже, чем у категорий

#     def items(self):
#         return Subcategory.objects.all()
    
#     def location(self, obj):
#         url = obj.get_absolute_url()
#         return url if url != '#' else None  # Исключаем подкатегории без категории

class SubcategoriesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6  # Можно сделать ниже, чем у категорий

    def items(self):
        """Возвращаем список кортежей (категория, подкатегория)."""
        pairs = []
        for subcategory in Subcategory.objects.all():
            for category in subcategory.categories.all():
                pairs.append((category, subcategory))
        return pairs
    
    def location(self, obj):
        category, subcategory = obj
        return reverse('social_cat', kwargs={'social': category.slug, 'category': subcategory.slug})



class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['index', 'contacts', 'services']

    def location(self, item):
        return f'/{item}/'