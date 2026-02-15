from django.contrib import admin
from .models import Category, Product, ProductImage, Size, ProductSize

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 4
    
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 3
    
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_filter = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug' : ('name',)}
    inlines = [ProductImageInline, ProductSizeInline ]
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}

# Register your models here.
