"""
Seed demo data for FinanceFlow screenshots.

Usage:
    python manage.py seed_demo                    # seeds for 'admin' user
    python manage.py seed_demo --user=test1       # seeds for specific user
    python manage.py seed_demo --clear            # wipes existing data first
"""
from datetime import date, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction as db_transaction

from finance.models import (
    Currency, UserCurrency, Category, Transaction, Budget
)


class Command(BaseCommand):
    help = "Seed demo transactions, budgets, and currencies for a user"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, default="admin",
                            help="Username to seed data for")
        parser.add_argument("--clear", action="store_true",
                            help="Delete existing transactions/budgets first")

    def handle(self, *args, **options):
        username = options["user"]
        clear = options["clear"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
            return

        self.stdout.write(f"Seeding data for: {user.username}")

        # ──── STEP 1: Ensure 5 currencies enabled ────
        wanted = ["NGN", "USD", "EUR", "GBP", "KES"]
        primary_code = "NGN"

        UserCurrency.objects.filter(user=user).delete()
        for i, code in enumerate(wanted):
            try:
                cur = Currency.objects.get(code=code)
            except Currency.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Currency {code} not seeded in DB"))
                continue
            UserCurrency.objects.create(
                user=user,
                currency=cur,
                is_primary=(code == primary_code),
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Enabled {len(wanted)} currencies"))

        # ──── STEP 2: Ensure categories exist ────
        needed_cats = {
            "Salary": ("income", "💰", "#10b981"),
            "Freelance": ("income", "💻", "#0ea5e9"),
            "Investments": ("income", "📈", "#8b5cf6"),
            "Groceries": ("expense", "🛒", "#f59e0b"),
            "Rent": ("expense", "🏠", "#ef4444"),
            "Transport": ("expense", "🚗", "#06b6d4"),
            "Dining Out": ("expense", "🍽️", "#ec4899"),
            "Utilities": ("expense", "💡", "#f97316"),
            "Healthcare": ("expense", "💊", "#14b8a6"),
            "Entertainment": ("expense", "🎬", "#a855f7"),
            "Shopping": ("expense", "🛍️", "#f43f5e"),
            "Subscriptions": ("expense", "💻", "#8b5cf6"),
        }

        cat_map = {}
        for name, (type_, icon, color) in needed_cats.items():
            cat, _ = Category.objects.get_or_create(
                user=user, name=name, type=type_,
                defaults={"icon": icon, "color": color},
            )
            cat_map[name] = cat
        self.stdout.write(self.style.SUCCESS(f"  ✓ Ensured {len(needed_cats)} categories"))

        # ──── STEP 3: Clear existing data if requested ────
        if clear:
            Transaction.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING("  ✓ Cleared existing data"))

        # ──── STEP 4: Build 6 months of transactions ────
        today = date.today()
        transactions = []

        # Helper: get a day in month N months ago
        def days_ago(n):
            return today - timedelta(days=n)

        # ── NGN (primary currency) ──
        ngn = Currency.objects.get(code="NGN")

        # 6 months of salary (today-ish each month)
        for m in range(6):
            day = (today.replace(day=5) - timedelta(days=30 * m))
            transactions.append(dict(
                currency=ngn, type="income", amount=Decimal("650000.00"),
                date=day, category=cat_map["Salary"],
                description=f"Monthly salary",
            ))

        # Freelance income (sparse)
        transactions += [
            dict(currency=ngn, type="income", amount=Decimal("180000.00"),
                 date=days_ago(45), category=cat_map["Freelance"],
                 description="Logo design gig"),
            dict(currency=ngn, type="income", amount=Decimal("95000.00"),
                 date=days_ago(12), category=cat_map["Freelance"],
                 description="Website tweaks"),
            dict(currency=ngn, type="income", amount=Decimal("250000.00"),
                 date=days_ago(3), category=cat_map["Freelance"],
                 description="Consulting session"),
        ]

        # Monthly rent
        for m in range(6):
            day = (today.replace(day=1) - timedelta(days=30 * m))
            transactions.append(dict(
                currency=ngn, type="expense", amount=Decimal("150000.00"),
                date=day, category=cat_map["Rent"],
                description="Monthly rent",
            ))

        # Groceries (weekly, last 6 months = ~26 entries)
        for w in range(26):
            transactions.append(dict(
                currency=ngn, type="expense",
                amount=Decimal(str(random.randint(22000, 55000))),
                date=days_ago(7 * w + random.randint(0, 3)),
                category=cat_map["Groceries"],
                description=random.choice([
                    "Weekly shopping", "Market run",
                    "Supermarket", "Local market",
                ]),
            ))

        # Dining (sparse)
        for _ in range(15):
            transactions.append(dict(
                currency=ngn, type="expense",
                amount=Decimal(str(random.randint(5000, 25000))),
                date=days_ago(random.randint(0, 180)),
                category=cat_map["Dining Out"],
                description=random.choice([
                    "Dinner with friends", "Lunch out",
                    "Coffee meeting", "Family dinner",
                ]),
            ))

        # Utilities (monthly)
        for m in range(6):
            transactions.append(dict(
                currency=ngn, type="expense",
                amount=Decimal(str(random.randint(15000, 35000))),
                date=(today.replace(day=10) - timedelta(days=30 * m)),
                category=cat_map["Utilities"],
                description="Electricity bill",
            ))

        # Transport (frequent)
        for _ in range(30):
            transactions.append(dict(
                currency=ngn, type="expense",
                amount=Decimal(str(random.randint(3000, 12000))),
                date=days_ago(random.randint(0, 180)),
                category=cat_map["Transport"],
                description=random.choice([
                    "Fuel top-up", "Uber ride", "Bus fare", "Bolt",
                ]),
            ))

        # Healthcare (sparse)
        transactions += [
            dict(currency=ngn, type="expense", amount=Decimal("18900.00"),
                 date=days_ago(30), category=cat_map["Healthcare"],
                 description="Pharmacy"),
            dict(currency=ngn, type="expense", amount=Decimal("45000.00"),
                 date=days_ago(90), category=cat_map["Healthcare"],
                 description="Health checkup"),
        ]

        # ── USD ──
        usd = Currency.objects.get(code="USD")

        # USD freelance income
        transactions += [
            dict(currency=usd, type="income", amount=Decimal("1800.00"),
                 date=days_ago(5), category=cat_map["Freelance"],
                 description="Upwork project"),
            dict(currency=usd, type="income", amount=Decimal("2400.00"),
                 date=days_ago(35), category=cat_map["Freelance"],
                 description="Fiverr order"),
            dict(currency=usd, type="income", amount=Decimal("1200.00"),
                 date=days_ago(65), category=cat_map["Freelance"],
                 description="Client retainer"),
            dict(currency=usd, type="income", amount=Decimal("500.00"),
                 date=days_ago(20), category=cat_map["Investments"],
                 description="Dividend payout"),
        ]

        # USD subscriptions
        for m in range(6):
            transactions += [
                dict(currency=usd, type="expense", amount=Decimal("45.00"),
                     date=(today.replace(day=15) - timedelta(days=30 * m)),
                     category=cat_map["Subscriptions"],
                     description="GitHub Copilot"),
                dict(currency=usd, type="expense", amount=Decimal("22.00"),
                     date=(today.replace(day=18) - timedelta(days=30 * m)),
                     category=cat_map["Entertainment"],
                     description="Netflix + Spotify"),
            ]

        # ── EUR ──
        eur = Currency.objects.get(code="EUR")

        transactions += [
            dict(currency=eur, type="income", amount=Decimal("750.00"),
                 date=days_ago(15), category=cat_map["Freelance"],
                 description="EU consulting"),
            dict(currency=eur, type="expense", amount=Decimal("180.00"),
                 date=days_ago(40), category=cat_map["Shopping"],
                 description="Amazon EU"),
            dict(currency=eur, type="expense", amount=Decimal("65.00"),
                 date=days_ago(8), category=cat_map["Dining Out"],
                 description="Restaurant Berlin"),
        ]

        # ── GBP ──
        gbp = Currency.objects.get(code="GBP")

        transactions += [
            dict(currency=gbp, type="income", amount=Decimal("5000.00"),
                 date=days_ago(10), category=cat_map["Freelance"],
                 description="UK client project"),
            dict(currency=gbp, type="income", amount=Decimal("1200.00"),
                 date=days_ago(50), category=cat_map["Investments"],
                 description="ISA dividend"),
            dict(currency=gbp, type="expense", amount=Decimal("2000.00"),
                 date=days_ago(25), category=cat_map["Rent"],
                 description="London apartment"),
            dict(currency=gbp, type="expense", amount=Decimal("95.00"),
                 date=days_ago(4), category=cat_map["Entertainment"],
                 description="Theatre tickets"),
        ]

        # ── KES ──
        kes = Currency.objects.get(code="KES")

        transactions += [
            dict(currency=kes, type="income", amount=Decimal("85000.00"),
                 date=days_ago(7), category=cat_map["Freelance"],
                 description="Nairobi project"),
            dict(currency=kes, type="expense", amount=Decimal("12000.00"),
                 date=days_ago(20), category=cat_map["Transport"],
                 description="Matatu + fuel"),
            dict(currency=kes, type="expense", amount=Decimal("35000.00"),
                 date=days_ago(12), category=cat_map["Rent"],
                 description="Airbnb Nairobi"),
        ]

        # ── Save all transactions ──
        for t in transactions:
            Transaction.objects.create(
                user=user, currency=t["currency"], type=t["type"],
                amount=t["amount"], date=t["date"], category=t["category"],
                description=t["description"], notes="",
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {len(transactions)} transactions"))

        # ──── STEP 5: Create budgets for current month ────
        current_month = today.month
        current_year = today.year

        budgets_data = [
            ("Groceries", ngn, Decimal("250000.00")),
            ("Rent", ngn, Decimal("150000.00")),
            ("Dining Out", ngn, Decimal("80000.00")),
            ("Transport", ngn, Decimal("60000.00")),
            ("Utilities", ngn, Decimal("50000.00")),
            ("Subscriptions", usd, Decimal("100.00")),
            ("Entertainment", usd, Decimal("80.00")),
            ("Rent", gbp, Decimal("2000.00")),
        ]

        for cat_name, currency, amount in budgets_data:
            Budget.objects.get_or_create(
                user=user,
                category=cat_map[cat_name],
                currency=currency,
                month=current_month,
                year=current_year,
                defaults={"amount": amount},
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {len(budgets_data)} budgets"))

        # ──── Done ────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS(f"  Demo data seeded for {user.username}"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(f"  Currencies: NGN (primary), USD, EUR, GBP, KES")
        self.stdout.write(f"  Transactions: {len(transactions)}")
        self.stdout.write(f"  Budgets: {len(budgets_data)}")
        self.stdout.write("")
        self.stdout.write("  Login and visit /dashboard/ to see it in action")
        self.stdout.write("")