from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from my_site.models import Service

class ServiceSitemap(Sitemap):
    changefreq = "never"
    priority = 0.8

    def items(self):
        return Service.objects.all()
    
    def location(self, obj):
        return f'{obj.get_absolute_url()}'

class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['index', 'contacts', 'services']

    def location(self, item):
        return f'/{item}/'