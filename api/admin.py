"""
Django Admin configuration for all SmartEcoSystem models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Category, Product, Order, Expense,
    Task, Message, Investment, Transaction, BusinessSettings,
    Business
)


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'role', 'company', 'balance', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('email', 'name', 'company')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'avatar', 'company')}),
        ('Role & Finance', {'fields': ('role', 'balance', 'equity_percent')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stock', 'buy_price', 'sell_price', 'is_low_stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'staff', 'amount', 'platform', 'status', 'created_at')
    list_filter = ('status', 'platform', 'created_at')
    search_fields = ('product__name', 'staff__name', 'note')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'category', 'amount', 'submitted_by', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('description', 'submitted_by__name')
    readonly_fields = ('created_at', 'updated_at')

    def approve(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user)
    approve.short_description = "Approve selected expenses"

    actions = ['approve']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'due_date', 'status', 'created_at')
    list_filter = ('status', 'due_date')
    search_fields = ('title', 'assigned_to__name', 'assigned_by__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__name', 'receiver__name', 'content')
    readonly_fields = ('created_at',)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('investor', 'amount', 'equity_percent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('investor__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'from_user', 'to_user', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('from_user__name', 'to_user__name', 'note')
    readonly_fields = ('created_at',)


@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'currency', 'tax_rate', 'updated_at')
