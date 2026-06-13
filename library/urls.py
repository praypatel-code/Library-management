from django.urls import path
from . import views

app_name = "library"   # <--- important so {% url 'library:...' %} works in templates

urlpatterns = [
    # authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # dashboard
    path("", views.dashboard, name="dashboard"),

    # authors
    path("authors/", views.author_list, name="author_list"),
    path("authors/add/", views.add_author, name="add_author"),
    path("authors/<int:author_id>/edit/", views.edit_author, name="edit_author"),
    path("authors/<int:author_id>/delete/", views.delete_author, name="delete_author"),

    # books
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.add_book, name="add_book"),
    path("books/<int:book_id>/edit/", views.edit_book, name="edit_book"),
    path("books/<int:book_id>/delete/", views.delete_book, name="delete_book"),

    # students
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.add_student, name="add_student"),
    path("students/<int:student_id>/edit/", views.edit_student, name="edit_student"),

    # circulation
    path("issue/", views.issue_book, name="issue_book"),
    path("return/", views.return_book, name="return_book"),
    path("issued/", views.issued_book_list, name="issued_book_list"),
    path("fines/", views.fine_list, name="fine_list"),
]
