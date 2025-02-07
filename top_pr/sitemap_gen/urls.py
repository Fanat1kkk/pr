from django.contrib.sitemaps.views import sitemap
from django.urls import path
from .sitemaps import ServiceSitemap, StaticSitemap

sitemaps = {
    'services': ServiceSitemap(),
    'static': StaticSitemap(),
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]