from django.contrib import admin

from item.models import Category, Item


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('_id', 'name')
    search_fields = ('_id', 'name')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'subCategory', 'progressStatus')
    search_fields = ('id', 'name')
    list_filter = ('category', 'subCategory',)
