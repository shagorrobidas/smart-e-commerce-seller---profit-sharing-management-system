from django.core.management.base import BaseCommand
from api.models import User, BusinessSettings, Category, Product, Order, Expense, Task
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds initial data for SmartEcoSystem development.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Create Business Settings
        settings = BusinessSettings.get_settings()
        settings.business_name = "SmartEcoSystem Demo"
        settings.currency = "BDT"
        settings.save()
        self.stdout.write(self.style.SUCCESS("Business settings created."))

        # 2. Create Users
        admin, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "name": "Super Admin",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "company": "SmartEco Corp",
            }
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"Admin created: {admin.email} / admin123"))

        staff, created = User.objects.get_or_create(
            email="staff@example.com",
            defaults={
                "name": "Staff Member",
                "role": "staff",
                "company": "SmartEco Corp",
            }
        )
        if created:
            staff.set_password("staff123")
            staff.save()
            self.stdout.write(self.style.SUCCESS(f"Staff created: {staff.email} / staff123"))

        investor, created = User.objects.get_or_create(
            email="investor@example.com",
            defaults={
                "name": "Lead Investor",
                "role": "investor",
                "equity_percent": 40.0,
                "company": "Green Capital",
            }
        )
        if created:
            investor.set_password("investor123")
            investor.save()
            self.stdout.write(self.style.SUCCESS(f"Investor created: {investor.email} / investor123"))

        # 3. Create Categories & Products
        cats = ["Electronics", "Home Decor", "Gadgets", "Fashion"]
        cat_objs = []
        for name in cats:
            c, _ = Category.objects.get_or_create(name=name)
            cat_objs.append(c)

        products = [
            ("Wireless Mouse", "Electronics", 50, 450, 850),
            ("Smart Watch", "Gadgets", 30, 1500, 2800),
            ("LED Lamp", "Home Decor", 20, 1200, 2200),
            ("Leather Wallet", "Fashion", 15, 800, 1500),
        ]

        for p_name, c_name, stock, buy, sell in products:
            cat = Category.objects.get(name=c_name)
            Product.objects.get_or_create(
                name=p_name,
                defaults={
                    "category": cat,
                    "stock": stock,
                    "buy_price": buy,
                    "sell_price": sell,
                    "added_by": admin
                }
            )
        self.stdout.write(self.style.SUCCESS("Categories and products seeded."))

        # 4. Create some tasks
        Task.objects.get_or_create(
            title="Update Inventory",
            defaults={
                "assigned_to": staff,
                "assigned_by": admin,
                "due_date": timezone.now().date() + timedelta(days=2),
                "status": "pending"
            }
        )
        self.stdout.write(self.style.SUCCESS("Tasks seeded."))

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
