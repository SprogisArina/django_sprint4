from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не указано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'is_published',
        'location',
        'category',
        'pub_date',
        'created_at'
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_display_links = ('title',)
    list_filter = (
        'category', 'location'
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'description',
        'slug',
        'created_at'
    )
    list_editable = (
        'is_published', 'description'
    )
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
