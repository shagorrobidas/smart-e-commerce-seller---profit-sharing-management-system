"""
SmartEcoSystem – All Database Models
Lives in the shared `api` app.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for the User model with no username field."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Extended user model with role-based access."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('investor', 'Investor'),
    ]
    username = None  # Use email as primary identifier
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    company = models.CharField(max_length=200, blank=True, default='')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    equity_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Investor's equity percentage (e.g. 40.00)"
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.name} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_investor(self):
        return self.role == 'investor'


class Business(models.Model):
    """Registered businesses/companies in the system."""
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Businesses'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Inventory product."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products'
    )
    stock = models.PositiveIntegerField(default=0)
    buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='products_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock <= 10

    @property
    def profit_per_unit(self):
        return self.sell_price - self.buy_price


class Order(models.Model):
    """Sales record / Order placed."""
    PLATFORM_CHOICES = [
        ('Daraz', 'Daraz'),
        ('CartUp', 'CartUp'),
        ('Offline', 'Offline/Direct'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name='orders'
    )
    staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='orders_recorded'
    )
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='Daraz')
    note = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='order_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order#{self.id} – {self.amount} ({self.platform})"


class Expense(models.Model):
    """Staff-submitted expense records."""
    CATEGORY_CHOICES = [
        ('Ops', 'Operations'),
        ('Marketing', 'Marketing'),
        ('Logistics', 'Logistics'),
        ('IT', 'IT & Technology'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    description = models.CharField(max_length=300)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Ops')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='expense_docs/', null=True, blank=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='expenses_submitted'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='expenses_approved'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.description} – {self.amount} [{self.status}]"


class Task(models.Model):
    """Task assigned by admin to staff."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='')
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_assigned'
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='tasks_created'
    )
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return f"{self.title} → {self.assigned_to.name}"

    @property
    def is_overdue(self):
        from datetime import date
        return self.due_date < date.today() and self.status != 'completed'


class Message(models.Model):
    """Internal messaging between users."""
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='messages_sent'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='messages_received'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.name} → {self.receiver.name}: {self.content[:50]}"


class Investment(models.Model):
    """Capital injection proposals from investors."""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    investor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='investments'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    equity_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Proposed equity increase percentage"
    )
    notes = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='investments_reviewed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Investment by {self.investor.name}: {self.amount} [{self.status}]"


class Transaction(models.Model):
    """Financial audit trail for all money movements."""
    TYPE_CHOICES = [
        ('sale', 'Sale Revenue'),
        ('expense', 'Expense'),
        ('profit_share', 'Profit Share'),
        ('investment', 'Investment'),
        ('transfer', 'Transfer'),
        ('refund', 'Refund'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    from_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions_sent'
    )
    to_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions_received'
    )
    note = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    reference_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions'
    )
    reference_expense = models.ForeignKey(
        Expense, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type.upper()} – {self.amount} [{self.status}]"


class BusinessSettings(models.Model):
    """Singleton model for global business configuration."""
    business_name = models.CharField(max_length=200, default='SmartSeller.sys')
    currency = models.CharField(max_length=10, default='BDT')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    announcement = models.TextField(blank=True, default='Welcome to the system!')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business Settings'
        verbose_name_plural = 'Business Settings'

    def __str__(self):
        return f"Settings: {self.business_name}"

    @classmethod
    def get_settings(cls):
        """Returns default settings if none exist."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
