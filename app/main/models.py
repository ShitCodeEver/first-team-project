from django.db import models
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=200, unique=True)
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
class Size(models.Model):
    name = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'Size'
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'
        
    def __str__(self):
        return self.name
    
class ProductSize(models.Model):
    size = models.ForeignKey(Size, on_delete=models.Model, related_name='sizes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='productsize')

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=200, unique=True)
    #price = models.DecimalField(max_digits=10, decimal_places=2) пусть будет цена будет привязана к цене
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='product/main/', null=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'Product'
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images')
    image = models.ImageField(upload_to='product/extra/')
