from django.contrib import admin

from books.models import Book, Category, Role, Contributor, BookContribution, ReadingList

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Role)
admin.site.register(Contributor)
admin.site.register(BookContribution)
admin.site.register(ReadingList)




