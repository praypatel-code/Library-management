from django.db import models
from django.utils import timezone

class Author(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="authors/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    CATEGORY_CHOICES = [
        ("Fiction", "Fiction"),
        ("Non-Fiction", "Non-Fiction"),
        ("Science", "Science"),
        ("Technology", "Technology"),
        ("History", "History"),
        ("Biography", "Biography"),
        ("Other", "Other"),
    ]
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="books/", blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    isbn = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    description = models.TextField(blank=True)
    publication_date = models.DateField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} ({self.author.name})"

class Student(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    address = models.TextField()
    photo = models.ImageField(upload_to="students/", blank=True, null=True)
    dob = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.phone}"

class Issue(models.Model):
    STATUS = (
        ("ISSUED", "Issued"),
        ("RETURNED", "Returned"),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="issues")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issues")
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(blank=True, null=True)
    return_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default="ISSUED")
    fine = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.issue_date + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        ref = self.return_date or timezone.now()
        return ref > (self.due_date or self.issue_date + timezone.timedelta(days=7))

    def calculate_fine(self):
        # 50 per day beyond 7 days (i.e., beyond due_date)
        ref_return = self.return_date or timezone.now()
        days_over = (ref_return.date() - (self.due_date.date() if self.due_date else self.issue_date.date())).days
        return 50 * max(0, days_over)
