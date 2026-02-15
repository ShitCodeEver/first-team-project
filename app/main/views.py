from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
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
    template_name = 'main/base.html'
    
    FILTER_MAPPING = { #короче это фильтер, лямбда нужна что бы проебашить все объекты
    'name': lambda queryset, value: queryset.filter(name__iexact=value), #предписка i-что-то, нужна для игнорирования реестра
    'price': lambda queryset, value: queryset.filter(price__gte=value),
    'max_price': lambda queryset, value: queryset.filter(price__lte=value),
    'description': lambda queryset, value: queryset.filter(description__icontains=value),
    'desc_start': lambda queryset, value: queryset.filter(description__istartswith=value), #типо поиск по первому слову, ну удобно хули
    }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('category_slug')
        current_category = None #выбраная категория типа
        products = Product.objects.all()# Фильтруем по категории, сюда можно впихнуть фильтр по дате, но похуй
        categories = Category.objects.all() #берем все категории
        
        if slug:
            current_category = get_object_or_404(Category, slug = slug)
            products = products.filter(Category=slug)
            
        query = self.request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains = query) | Q(description__incontains = query)
            )
        filter_params = {} #инициализируем словарь, что бы был
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products,value)
                filter_params[param] = value
            else:
                filter_params[param] = ''
                
        filter_params['q'] = query or ''
        
        context.update({
            'categories' : categories,
            'products' : products,
            'current_category': slug,
            'filter_params': filter_params,
            #'sizes': Size.objects.all(), такую конструкцию можно использовать для доп объектов или конструкций
            'search_query': query or ''
        })
        
        if self.request.GET.get('slow_search') == 'true': #короче, наш поисковик
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['reset_search'] = True
            
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/product_list.html', context)
        return TemplateResponse(request, self.template_name, context)
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/base.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['categories'] = Category.objects.all()
        context['related_product'] = Product.objects.filter(
            Category=product.category
        ).exclude(id=product.id)[:4]
        context['current_category'] = product.category.slug
        return context
    
    def get(self, request, *args, **kwargs): #цель функции проверить, существует ли товар
        context = self.get_context_data(**kwargs) #передаем данные
        if request.headers.get('HX-Request'): #если это HTMX запрос
            return TemplateResponse(request, 'main/home_content.html', context) #если да, то выводим блок
        return TemplateResponse(request, self.template_name, context) #выводим страницу, всегда