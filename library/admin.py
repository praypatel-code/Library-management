from django.contrib import admin
from .models import Author, Book, Student, Issue

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "category", "total_copies", "available_copies")
    list_filter = ("category", "author")
    search_fields = ("title", "isbn")

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("book", "student", "status", "issue_date", "due_date", "return_date", "fine")
    list_filter = ("status",)
    search_fields = ("book__title", "student__name", "student__phone", "student__email")
