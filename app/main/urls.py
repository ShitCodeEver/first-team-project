from django.urls import path
from django.conf.urls.static import static
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('catalog/', views.CatalogView.as_view(), name='catalog_all'),
    path('catalog/<slug:category_slug>/', views.CatalogView.as_view(), name='catalog'),
    path('catalog/<slug:category_slug>/<slug:slug>/', views.ProductDetailView.as_view(), name='product'),
    path('about/', views.AboutView.as_view(), name='about_page'),
]
