from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from .models import Category, Product, Size
from django.db.models import Q

# Create your views here.
class IndexView(TemplateView): #посути метод получения данных
    template_name = 'main/base.html' #базовая верстка, чьи элементы можно менять
    
    def get_context_data(self, **kwargs): #получения данных
        context = super().get_context_data(**kwargs) #получения аргументов
        context['categories'] = Category.objects.all() # получение всех объектов класс
        context['current_category'] = None #всегда остается пустым
        return context
    
    def get(self, request, *args, **kwargs): #цель функции проверить, существует ли товар
        context = self.get_context_data(**kwargs) #передаем данные
        if request.headers.get('HX-Request'): #если это HTMX запрос
            return TemplateResponse(request, 'main/home_content.html', context) #если да, то выводим блок
        return TemplateResponse(request, self.template_name, context) #выводим страницу, всегда
    
class CatalogView(TemplateView):
    template_name = 'main/catalog.html'
    
    FILTER_MAPPING = {
        'name': lambda queryset, value: queryset.filter(name__iexact=value),
        'size': lambda queryset, value: queryset.filter(productsize__size__name__iexact=value).distinct(),
        'description': lambda queryset, value: queryset.filter(description__icontains=value),
        'desc_start': lambda queryset, value: queryset.filter(description__istartswith=value),
        'min_price': lambda queryset, value: queryset.filter(productsize__price__gte=value).distinct(),
        'max_price': lambda queryset, value: queryset.filter(productsize__price__lte=value).distinct(),
    }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('category_slug')
        
        products = Product.objects.select_related('category').prefetch_related('productsize__size').all()
        categories = Category.objects.all()
        
        
        current_category_obj = None
        if slug:
            current_category_obj = get_object_or_404(Category, slug=slug)
            products = products.filter(category=current_category_obj)
                                       
        query = self.request.GET.get('q')
        if query:
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ''
                
        context.update({
            'categories': categories,
            'products': products,
            'current_category': slug, # передаем строку слага для URL-ов
            'filter_params': filter_params,
            'search_query': query or ''
        })
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            # Предположим, тут список карточек товаров
            return TemplateResponse(request, 'main/product_list.html', context)
        return TemplateResponse(request, self.template_name, context)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug' 

    def get_object(self, queryset=None):
        # Ищем продукт, проверяя что слаг категории в URL совпадает с реальной категорией товара
        return get_object_or_404(
            Product, 
            slug=self.kwargs.get('slug'), 
            category__slug=self.kwargs.get('category_slug')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['categories'] = Category.objects.all()
        context['related_product'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        context['current_category'] = product.category.slug
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if request.headers.get('HX-Request'):
            # Здесь должен быть шаблон ТОЛЬКО с контентом страницы товара
            return TemplateResponse(request, 'main/base.html', context)
        return TemplateResponse(request, self.template_name, context)
    
class AboutView(TemplateView): #посути блок, ыыы
    template_name = 'main/about.html'  # Полная страница

    def get(self, request, *args, **kwargs):
        # Если прилетел запрос от HTMX (например, нажали на ссылку в меню)
        if request.headers.get('HX-Request'):
            # Отдаем ТОЛЬКО кусок с контентом
            return TemplateResponse(request, 'main/about_content.html')
        # Если юзер просто вбил адрес в строку или обновил страницу (F5)
        return super().get(request, *args, **kwargs)