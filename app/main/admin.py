from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 4
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description']
    list_filter = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug' : ('name',)}
    inlines = [ProductImageInline]
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}
    
# Register your models here.
