from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import Author, Book, Student, Issue

# ---------- Auth ----------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        p1 = request.POST.get("password1", "")
        p2 = request.POST.get("password2", "")
        if not username or not p1:
            messages.error(request, "Username and password are required.")
        elif p1 != p2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=p1)
            messages.success(request, "Registration successful. Please login.")
            return redirect("library:login")
    return render(request, 
                  "library/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("library:dashboard")
        messages.error(request, "Invalid credentials.")
    return render(request, "library/login.html")

def logout_view(request):
    logout(request)
    return redirect("library:login")

# ---------- Dashboard ----------
@login_required
def dashboard(request):
    author_count = Author.objects.count()
    book_count = Book.objects.aggregate(total=Sum("total_copies"))["total"] or 0
    student_count = Student.objects.count()
    context = {
        "author_count": author_count,
        "book_count": book_count,
        "student_count": student_count,
    }
    return render(request, "library/dashboard.html", context)

# ---------- Authors ----------
@login_required
def author_list(request):
    authors = Author.objects.all()
    return render(request, "library/author_list.html", {"authors": authors})

@login_required
def add_author(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        bio = request.POST.get("bio", "").strip()
        photo = request.FILES.get("photo")
        if not name:
            messages.error(request, "Name is required.")
        else:
            Author.objects.create(name=name, bio=bio, photo=photo)
            messages.success(request, "Author added.")
            return redirect("library:add_author")
    return render(request, "library/add_author.html")

@login_required
def edit_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == "POST":
        author.name = request.POST.get("name", author.name).strip()
        author.bio = request.POST.get("bio", author.bio).strip()
        if request.FILES.get("photo"):
            author.photo = request.FILES["photo"]
        author.save()
        messages.success(request, "Author updated.")
        return redirect("library:edit_author", author_id=author.id)
    return render(request, "library/edit_author.html", {"author": author})

def delete_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    messages.success(request, "author deleted successfully.")
    return redirect("library:author_list")

# ---------- Books ----------
def book_list(request):
    books = Book.objects.select_related("author").all()
    return render(request, "library/book_list.html", {"books": books})

@login_required
def add_book(request):
    authors = Author.objects.all().order_by("name")
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        image = request.FILES.get("image")
        author_id = request.POST.get("author")
        isbn = request.POST.get("isbn", "").strip()
        category = request.POST.get("category", "Other")
        description = request.POST.get("description", "")
        publication_date = request.POST.get("publication_date")
        total_copies = int(request.POST.get("total_copies") or 1)
        if not (title and author_id and isbn):
            messages.error(request, "Title, Author and ISBN are required.")
        else:
            author = get_object_or_404(Author, id=author_id)
            book = Book(
                title=title, image=image, author=author, isbn=isbn, category=category,
                description=description, total_copies=total_copies, available_copies=total_copies
            )
            if publication_date:
                book.publication_date = publication_date
            book.save()
            messages.success(request, "Book added.")
            return redirect("library:add_book")
    return render(request, "library/add_book.html", {"authors": authors})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    authors = Author.objects.all().order_by("name")
    if request.method == "POST":
        book.title = request.POST.get("title", book.title).strip()
        if request.FILES.get("image"):
            book.image = request.FILES["image"]
        author_id = request.POST.get("author")
        if author_id:
            book.author = get_object_or_404(Author, id=author_id)
        book.isbn = request.POST.get("isbn", book.isbn).strip()
        book.category = request.POST.get("category", book.category)
        book.description = request.POST.get("description", book.description)
        pd = request.POST.get("publication_date")
        if pd:
            book.publication_date = pd
        total = int(request.POST.get("total_copies") or book.total_copies)
        # adjust available if total changed: keep current loans intact
        delta = total - book.total_copies
        book.total_copies = total
        book.available_copies = max(0, book.available_copies + delta)
        book.save()
        messages.success(request, "Book updated.")
        return redirect("library:edit_book", book_id=book.id)
    return render(request, "library/edit_book.html", {"book": book, "authors": authors})

# ---------- Students ----------
@login_required
def add_student(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        photo = request.FILES.get("photo")
        dob = request.POST.get("dob")
        if not (name and phone and email and address and dob):
            messages.error(request, "All fields except photo are required.")
        else:
            Student.objects.create(
                name=name, phone=phone, email=email, address=address, photo=photo, dob=dob
            )
            messages.success(request, "Student added.")
            return redirect("library:add_student")
    return render(request, "library/add_student.html")

@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student.name = request.POST.get("name", student.name).strip()
        student.phone = request.POST.get("phone", student.phone).strip()
        student.email = request.POST.get("email", student.email).strip()
        student.address = request.POST.get("address", student.address).strip()
        if request.FILES.get("photo"):
            student.photo = request.FILES["photo"]
        dob = request.POST.get("dob")
        if dob:
            student.dob = dob
        student.save()
        messages.success(request, "Student updated.")
        return redirect("library:edit_student", student_id=student.id)
    return render(request, "library/edit_student.html", {"student": student})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, "Book deleted successfully.")
    return redirect("library:book_list")

@login_required
def student_list(request):
    q = request.GET.get("q", "").strip()
    students = Student.objects.all().order_by("name")
    if q:
        students = students.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q))
    return render(request, "library/student_list.html", {"students": students, "q": q})

# ---------- Issue / Return ----------
@login_required
def issue_book(request):
    # Only show books with available_copies > 0
    books = Book.objects.filter(available_copies__gt=0).order_by("title")
    students = Student.objects.all().order_by("name")
    if request.method == "POST":
        student_id = request.POST.get("student")
        book_id = request.POST.get("book")
        if not (student_id and book_id):
            messages.error(request, "Student and Book are required.")
        else:
            student = get_object_or_404(Student, id=student_id)
            book = get_object_or_404(Book, id=book_id)
            if book.available_copies <= 0:
                messages.error(request, "Selected book is not available.")
            else:
                issue = Issue.objects.create(student=student, book=book)
                book.available_copies -= 1
                book.save()
                messages.success(request, f"Issued: {book.title} to {student.name}.")
                return redirect("library:issue_book")
    return render(request, "library/issue_book.html", {"books": books, "students": students})

@login_required
def issued_book_list(request):
    issues = Issue.objects.select_related("book", "student").order_by("-issue_date")
    return render(request, "library/issued_book_list.html", {"issues": issues})

@login_required
def return_book(request):
    if request.method == "POST":
        issue_id = request.POST.get("issue_id")
        issue = get_object_or_404(Issue, id=issue_id, status="ISSUED")
        issue.return_date = timezone.now()
        # calculate fine
        issue.fine = issue.calculate_fine()
        issue.status = "RETURNED"
        issue.save()
        # increment availability
        book = issue.book
        book.available_copies = min(book.total_copies, book.available_copies + 1)
        book.save()
        messages.success(request, f"Returned: {book.title}. Fine: ₹{issue.fine}.")
        return redirect("library:return_book")
    # show only currently issued (not returned)
    active_issues = Issue.objects.filter(status="ISSUED").select_related("book", "student")
    return render(request, "library/return_book.html", {"active_issues": active_issues})

@login_required
def fine_list(request):
    fines = Issue.objects.filter(fine__gt=0).select_related("book", "student").order_by("-return_date", "-fine")
    return render(request, "library/fine_list.html", {"fines": fines})
