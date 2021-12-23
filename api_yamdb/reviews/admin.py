from django.contrib import admin

from .models import User, Category, Genre, Title, GenreTitle, Review, Comment

class UserAdmin(admin.ModelAdmin):
    list_display = ('bio', 'role')
    search_fields = ('bio',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category')
    #Добавить genre поле ManytoMany
    search_fields = ('description',)
    empty_value_display = '-пусто-'
    list_filter = ('year',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('title', 'text')
    empty_value_display = '-пусто-'
    list_filter = ('pub_date',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('title', 'text')
    empty_value_display = '-пусто-'
    list_filter = ('pub_date',)


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
