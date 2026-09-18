"""Rich demo data seeder — 6 months of history for ALL 5 currencies."""
from datetime import date, timedelta
from decimal import Decimal
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from finance.models import Currency, UserCurrency, Category, Transaction, Budget


class Command(BaseCommand):
    help = "Seed rich demo data (6 months, 5 currencies)"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, default="admin")
        parser.add_argument("--clear", action="store_true")

    def _day_in_month(self, months_ago, day):
        """Return a date N months ago, on `day` of that month (clamped)."""
        today = date.today()
        y, m = today.year, today.month - months_ago
        while m <= 0:
            m += 12
            y -= 1
        # clamp day to last day of that month
        from calendar import monthrange
        last = monthrange(y, m)[1]
        return date(y, m, min(day, last))

    def handle(self, *args, **options):
        random.seed(42)  # deterministic output
        username = options["user"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
            return

        self.stdout.write(f"Seeding rich data for: {user.username}")

        # ── 1. Enable 5 currencies ──
        wanted = ["NGN", "USD", "EUR", "GBP", "KES"]
        UserCurrency.objects.filter(user=user).delete()
        for code in wanted:
            try:
                cur = Currency.objects.get(code=code)
                UserCurrency.objects.create(user=user, currency=cur, is_primary=(code == "NGN"))
            except Currency.DoesNotExist:
                pass
        self.stdout.write(self.style.SUCCESS(f"  ✓ Enabled {len(wanted)} currencies"))

        # ── 2. Categories ──
        cats = {
            "Salary": ("income", "💰", "#10b981"),
            "Freelance": ("income", "💻", "#0ea5e9"),
            "Investments": ("income", "📈", "#8b5cf6"),
            "Gifts Received": ("income", "🎁", "#ec4899"),
            "Rent": ("expense", "🏠", "#ef4444"),
            "Groceries": ("expense", "🛒", "#f59e0b"),
            "Transport": ("expense", "🚗", "#06b6d4"),
            "Dining Out": ("expense", "🍽️", "#ec4899"),
            "Utilities": ("expense", "💡", "#f97316"),
            "Healthcare": ("expense", "💊", "#14b8a6"),
            "Entertainment": ("expense", "🎬", "#a855f7"),
            "Shopping": ("expense", "🛍️", "#f43f5e"),
            "Education": ("expense", "📚", "#3b82f6"),
            "Subscriptions": ("expense", "💻", "#8b5cf6"),
            "Fitness": ("expense", "🏋️", "#10b981"),
        }
        cmap = {}
        for name, (t, icon, color) in cats.items():
            c, _ = Category.objects.get_or_create(
                user=user, name=name, type=t,
                defaults={"icon": icon, "color": color},
            )
            cmap[name] = c

        if options["clear"]:
            Transaction.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING("  ✓ Cleared existing data"))

        NGN = Currency.objects.get(code="NGN")
        USD = Currency.objects.get(code="USD")
        EUR = Currency.objects.get(code="EUR")
        GBP = Currency.objects.get(code="GBP")
        KES = Currency.objects.get(code="KES")

        rows = []

        # ══════════════════════════════════════════════
        # NGN — primary, 6 months of rich activity
        # ══════════════════════════════════════════════
        for m in range(6):
            # Salary every month
            rows.append(dict(currency=NGN, type="income", amount=Decimal(str(random.randint(600000, 720000))),
                             date=self._day_in_month(m, 25), category=cmap["Salary"],
                             description=f"Monthly salary"))
            # Freelance income (varies)
            if m % 2 == 0:
                rows.append(dict(currency=NGN, type="income", amount=Decimal(str(random.randint(80000, 260000))),
                                 date=self._day_in_month(m, 8), category=cmap["Freelance"],
                                 description=random.choice(["Logo design", "Website tweaks", "Consulting", "Brand identity"])))
            # Investment income
            if m % 3 == 0:
                rows.append(dict(currency=NGN, type="income", amount=Decimal(str(random.randint(60000, 160000))),
                                 date=self._day_in_month(m, 12), category=cmap["Investments"],
                                 description="Treasury interest"))
            # Rent
            rows.append(dict(currency=NGN, type="expense", amount=Decimal("150000.00"),
                             date=self._day_in_month(m, 1), category=cmap["Rent"],
                             description="Monthly rent"))
            # Utilities
            rows.append(dict(currency=NGN, type="expense", amount=Decimal(str(random.randint(15000, 38000))),
                             date=self._day_in_month(m, 10), category=cmap["Utilities"],
                             description="Electricity"))
            rows.append(dict(currency=NGN, type="expense", amount=Decimal(str(random.randint(7000, 16000))),
                             date=self._day_in_month(m, 12), category=cmap["Utilities"],
                             description="Water"))
            # Groceries (4 per month)
            for w in range(4):
                rows.append(dict(currency=NGN, type="expense",
                                 amount=Decimal(str(random.randint(22000, 58000))),
                                 date=self._day_in_month(m, 3 + w * 7),
                                 category=cmap["Groceries"],
                                 description=random.choice(["Weekly shopping", "Market run", "Supermarket", "Local market"])))
            # Dining (3 per month)
            for _ in range(3):
                rows.append(dict(currency=NGN, type="expense",
                                 amount=Decimal(str(random.randint(4500, 26000))),
                                 date=self._day_in_month(m, random.randint(1, 28)),
                                 category=cmap["Dining Out"],
                                 description=random.choice(["Lunch out", "Dinner with friends", "Coffee meeting", "Brunch"])))
            # Transport (6 per month)
            for _ in range(6):
                rows.append(dict(currency=NGN, type="expense",
                                 amount=Decimal(str(random.randint(2500, 15000))),
                                 date=self._day_in_month(m, random.randint(1, 28)),
                                 category=cmap["Transport"],
                                 description=random.choice(["Fuel", "Uber", "Bolt", "Bus fare", "Keke", "Parking"])))
            # Entertainment (1 per month)
            rows.append(dict(currency=NGN, type="expense",
                             amount=Decimal(str(random.randint(8000, 35000))),
                             date=self._day_in_month(m, random.randint(5, 25)),
                             category=cmap["Entertainment"],
                             description=random.choice(["Cinema", "Concert", "Bowling", "Game night"])))
            # Fitness
            rows.append(dict(currency=NGN, type="expense", amount=Decimal("6500.00"),
                             date=self._day_in_month(m, 5),
                             category=cmap["Fitness"],
                             description="Gym membership"))
            # Healthcare occasionally
            if m % 2 == 1:
                rows.append(dict(currency=NGN, type="expense",
                                 amount=Decimal(str(random.randint(12000, 65000))),
                                 date=self._day_in_month(m, random.randint(3, 25)),
                                 category=cmap["Healthcare"],
                                 description=random.choice(["Pharmacy", "Checkup", "Lab tests", "Dental"])))
            # Shopping occasionally
            if m % 2 == 0:
                rows.append(dict(currency=NGN, type="expense",
                                 amount=Decimal(str(random.randint(25000, 140000))),
                                 date=self._day_in_month(m, random.randint(8, 25)),
                                 category=cmap["Shopping"],
                                 description=random.choice(["Clothing", "Electronics", "Home goods", "Shoes"])))

        # ══════════════════════════════════════════════
        # USD — 6 months of activity
        # ══════════════════════════════════════════════
        for m in range(6):
            # Freelance income monthly
            rows.append(dict(currency=USD, type="income",
                             amount=Decimal(str(random.randint(1200, 2800))),
                             date=self._day_in_month(m, 15),
                             category=cmap["Freelance"],
                             description=random.choice(["Upwork project", "Fiverr order", "Client retainer", "Consulting"])))
            # Investment dividend every 3rd month
            if m % 3 == 0:
                rows.append(dict(currency=USD, type="income",
                                 amount=Decimal(str(random.randint(300, 900))),
                                 date=self._day_in_month(m, 20),
                                 category=cmap["Investments"],
                                 description="Dividend payout"))
            # Subscriptions
            rows.append(dict(currency=USD, type="expense", amount=Decimal("45.00"),
                             date=self._day_in_month(m, 15),
                             category=cmap["Subscriptions"], description="GitHub Copilot"))
            rows.append(dict(currency=USD, type="expense", amount=Decimal("22.00"),
                             date=self._day_in_month(m, 18),
                             category=cmap["Subscriptions"], description="Netflix + Spotify"))
            rows.append(dict(currency=USD, type="expense", amount=Decimal("12.00"),
                             date=self._day_in_month(m, 22),
                             category=cmap["Subscriptions"], description="iCloud + Notion"))
            # Entertainment
            rows.append(dict(currency=USD, type="expense",
                             amount=Decimal(str(random.randint(40, 180))),
                             date=self._day_in_month(m, random.randint(3, 26)),
                             category=cmap["Entertainment"],
                             description=random.choice(["Steam games", "Kindle books", "Audible", "Movie rentals"])))
            # Shopping
            if m % 2 == 0:
                rows.append(dict(currency=USD, type="expense",
                                 amount=Decimal(str(random.randint(80, 450))),
                                 date=self._day_in_month(m, random.randint(5, 25)),
                                 category=cmap["Shopping"],
                                 description=random.choice(["Amazon order", "Gadget upgrade", "Clothing", "Books"])))

        # ══════════════════════════════════════════════
        # EUR — 6 months of activity
        # ══════════════════════════════════════════════
        for m in range(6):
            # Freelance income monthly
            rows.append(dict(currency=EUR, type="income",
                             amount=Decimal(str(random.randint(400, 900))),
                             date=self._day_in_month(m, 10),
                             category=cmap["Freelance"],
                             description=random.choice(["EU consulting", "Design work", "App translation"])))
            # Expenses
            rows.append(dict(currency=EUR, type="expense",
                             amount=Decimal(str(random.randint(60, 200))),
                             date=self._day_in_month(m, random.randint(2, 27)),
                             category=cmap["Dining Out"],
                             description=random.choice(["Restaurant Berlin", "Cafe Paris", "Lunch Amsterdam"])))
            rows.append(dict(currency=EUR, type="expense",
                             amount=Decimal(str(random.randint(40, 160))),
                             date=self._day_in_month(m, random.randint(5, 25)),
                             category=cmap["Transport"],
                             description=random.choice(["Train pass", "Metro ticket", "Bike rental"])))
            if m % 2 == 0:
                rows.append(dict(currency=EUR, type="expense",
                                 amount=Decimal(str(random.randint(100, 300))),
                                 date=self._day_in_month(m, random.randint(10, 26)),
                                 category=cmap["Shopping"],
                                 description=random.choice(["Amazon EU", "Clothing", "Souvenirs"])))

        # ══════════════════════════════════════════════
        # GBP — 6 months of activity
        # ══════════════════════════════════════════════
        for m in range(6):
            # Freelance income monthly
            rows.append(dict(currency=GBP, type="income",
                             amount=Decimal(str(random.randint(2500, 5500))),
                             date=self._day_in_month(m, 5),
                             category=cmap["Freelance"],
                             description="UK client project"))
            # Investment income
            if m % 3 == 0:
                rows.append(dict(currency=GBP, type="income",
                                 amount=Decimal(str(random.randint(800, 1600))),
                                 date=self._day_in_month(m, 20),
                                 category=cmap["Investments"],
                                 description="ISA dividend"))
            # Rent
            rows.append(dict(currency=GBP, type="expense", amount=Decimal("2000.00"),
                             date=self._day_in_month(m, 1),
                             category=cmap["Rent"], description="London rent"))
            # Expenses
            rows.append(dict(currency=GBP, type="expense",
                             amount=Decimal(str(random.randint(150, 380))),
                             date=self._day_in_month(m, 8),
                             category=cmap["Groceries"], description="Tesco shopping"))
            rows.append(dict(currency=GBP, type="expense",
                             amount=Decimal(str(random.randint(50, 120))),
                             date=self._day_in_month(m, random.randint(3, 26)),
                             category=cmap["Transport"], description="Tube top-up"))
            rows.append(dict(currency=GBP, type="expense",
                             amount=Decimal(str(random.randint(60, 220))),
                             date=self._day_in_month(m, random.randint(5, 25)),
                             category=cmap["Entertainment"],
                             description=random.choice(["Theatre tickets", "Pub night", "Cinema", "Concert"])))
            if m % 2 == 0:
                rows.append(dict(currency=GBP, type="expense",
                                 amount=Decimal(str(random.randint(80, 400))),
                                 date=self._day_in_month(m, random.randint(10, 25)),
                                 category=cmap["Shopping"],
                                 description=random.choice(["Winter coat", "Shoes", "Home goods"])))

        # ══════════════════════════════════════════════
        # KES — 6 months of activity
        # ══════════════════════════════════════════════
        for m in range(6):
            # Freelance income monthly
            rows.append(dict(currency=KES, type="income",
                             amount=Decimal(str(random.randint(50000, 120000))),
                             date=self._day_in_month(m, 12),
                             category=cmap["Freelance"],
                             description=random.choice(["Nairobi project", "Local freelance", "Consulting fee"])))
            # Rent
            rows.append(dict(currency=KES, type="expense",
                             amount=Decimal(str(random.randint(25000, 45000))),
                             date=self._day_in_month(m, 2),
                             category=cmap["Rent"], description="Airbnb Nairobi"))
            # Groceries
            rows.append(dict(currency=KES, type="expense",
                             amount=Decimal(str(random.randint(2000, 6000))),
                             date=self._day_in_month(m, 15),
                             category=cmap["Groceries"], description="Naivas shopping"))
            # Transport
            rows.append(dict(currency=KES, type="expense",
                             amount=Decimal(str(random.randint(1500, 4500))),
                             date=self._day_in_month(m, random.randint(5, 25)),
                             category=cmap["Transport"], description="Matatu + fuel"))
            # Dining
            rows.append(dict(currency=KES, type="expense",
                             amount=Decimal(str(random.randint(800, 3200))),
                             date=self._day_in_month(m, random.randint(3, 26)),
                             category=cmap["Dining Out"],
                             description=random.choice(["Mama Oliech", "Nyama Choma", "Java House"])))
            # Subscriptions
            rows.append(dict(currency=KES, type="expense",
                             amount=Decimal(str(random.randint(500, 1500))),
                             date=self._day_in_month(m, 20),
                             category=cmap["Subscriptions"], description="Safaricom bundle"))

        # ── Save all ──
        for t in rows:
            Transaction.objects.create(user=user, notes="", **t)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {len(rows)} transactions"))

        # ── Budgets for current month ──
        today = date.today()
        budgets = [
            ("Groceries", NGN, Decimal("250000")),
            ("Rent", NGN, Decimal("150000")),
            ("Dining Out", NGN, Decimal("90000")),
            ("Transport", NGN, Decimal("70000")),
            ("Utilities", NGN, Decimal("55000")),
            ("Entertainment", NGN, Decimal("40000")),
            ("Shopping", NGN, Decimal("150000")),
            ("Subscriptions", USD, Decimal("100")),
            ("Entertainment", USD, Decimal("250")),
            ("Shopping", USD, Decimal("400")),
            ("Rent", GBP, Decimal("2000")),
            ("Groceries", GBP, Decimal("400")),
            ("Shopping", EUR, Decimal("250")),
            ("Transport", EUR, Decimal("200")),
            ("Rent", KES, Decimal("45000")),
        ]
        for cn, cur, amt in budgets:
            Budget.objects.get_or_create(
                user=user, category=cmap[cn], currency=cur,
                month=today.month, year=today.year,
                defaults={"amount": amt},
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {len(budgets)} budgets"))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(self.style.SUCCESS(f"  ✅ Done"))
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(f"  Currencies: NGN ⭐ · USD · EUR · GBP · KES")
        self.stdout.write(f"  Transactions: {len(rows)}")
        self.stdout.write(f"  Budgets: {len(budgets)}")
        self.stdout.write(f"  Span: 6 months")
        self.stdout.write("")