from django.contrib import admin

from .models import Category, Location, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'title',
        'text',
    )
    list_filter = (
        'category',
        'author',
        'location'
    )


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Comment)
admin.site.register(Post, PostAdmin)
