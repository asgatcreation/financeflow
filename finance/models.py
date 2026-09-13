from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


# ═══════════════════════════════════════════════════════
# CURRENCIES
# ═══════════════════════════════════════════════════════
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=6)
    flag = models.CharField(max_length=8, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.code} · {self.name}"


class UserCurrency(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_currencies")
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "currency")
        ordering = ["-is_primary", "currency__code"]
        verbose_name_plural = "User currencies"

    def __str__(self):
        return f"{self.user.username} · {self.currency.code}"


# ═══════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════
class Category(models.Model):
    TYPE_CHOICES = [("income", "Income"), ("expense", "Expense")]

    ICON_CHOICES = [
        ("🍔", "Food"), ("🚗", "Transport"), ("🏠", "Rent"),
        ("💡", "Utilities"), ("🎬", "Entertainment"), ("💊", "Health"),
        ("🛒", "Shopping"), ("📚", "Education"), ("✈️", "Travel"),
        ("💰", "Salary"), ("🎁", "Gift"), ("📈", "Investment"),
        ("💻", "Subscriptions"), ("🏋️", "Fitness"), ("☕", "Coffee"),
        ("🛍️", "Retail"), ("🍽️", "Dining"), ("📱", "Phone"),
        ("🎓", "Tuition"), ("🚌", "Public Transport"), ("💳", "Other"),
    ]

    COLOR_CHOICES = [
        ("#10b981", "Emerald"), ("#0ea5e9", "Sky"), ("#8b5cf6", "Violet"),
        ("#ec4899", "Pink"), ("#ef4444", "Red"), ("#f59e0b", "Amber"),
        ("#06b6d4", "Cyan"), ("#3b82f6", "Blue"), ("#a855f7", "Purple"),
        ("#f97316", "Orange"), ("#14b8a6", "Teal"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=10, choices=ICON_CHOICES, default="💳")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="#10b981")
    is_default = models.BooleanField(default=False, help_text="Auto-created starter category")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name", "type")
        ordering = ["type", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.icon} {self.name} ({self.type})"

    def get_absolute_url(self):
        return reverse("finance:categories")


# ═══════════════════════════════════════════════════════
# TRANSACTIONS
# ═══════════════════════════════════════════════════════
class Transaction(models.Model):
    TYPE_CHOICES = [("income", "Income"), ("expense", "Expense")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="transactions"
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, null=True, blank=True,
        related_name="transactions"
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        sign = "+" if self.type == "income" else "-"
        cur = self.currency.code if self.currency else "?"
        return f"{sign}{cur} {self.amount} · {self.description}"

    def get_absolute_url(self):
        return reverse("finance:transactions")

    @property
    def signed_amount(self):
        return self.amount if self.type == "income" else -self.amount


# ═══════════════════════════════════════════════════════
# BUDGETS
# ═══════════════════════════════════════════════════════
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, null=True, blank=True,
        related_name="budgets"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "category", "currency", "month", "year")
        ordering = ["-year", "-month", "category__name"]

    def __str__(self):
        cur = self.currency.code if self.currency else "?"
        return f"{self.category.name} · {cur} {self.amount} · {self.month}/{self.year}"

    @property
    def spent(self):
        qs = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type="expense",
            date__month=self.month,
            date__year=self.year,
        )
        if self.currency:
            qs = qs.filter(currency=self.currency)
        return qs.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def remaining(self):
        return self.amount - self.spent

    @property
    def percent_used(self):
        if self.amount == 0:
            return 0
        return min(int((self.spent / self.amount) * 100), 100)

    @property
    def is_over(self):
        return self.spent > self.amount

    @property
    def is_warning(self):
        return not self.is_over and self.percent_used >= 80


# ═══════════════════════════════════════════════════════
# AUTO-SEED on user creation
# ═══════════════════════════════════════════════════════
DEFAULT_CATEGORIES = [
    # INCOME
    ("Salary", "income", "💰", "#10b981"),
    ("Freelance", "income", "💻", "#0ea5e9"),
    ("Investments", "income", "📈", "#8b5cf6"),
    ("Gifts Received", "income", "🎁", "#ec4899"),
    # EXPENSE
    ("Groceries", "expense", "🛒", "#f59e0b"),
    ("Rent", "expense", "🏠", "#ef4444"),
    ("Transport", "expense", "🚗", "#06b6d4"),
    ("Dining Out", "expense", "🍽️", "#ec4899"),
    ("Utilities", "expense", "💡", "#f97316"),
    ("Healthcare", "expense", "💊", "#14b8a6"),
    ("Entertainment", "expense", "🎬", "#a855f7"),
    ("Shopping", "expense", "🛍️", "#f43f5e"),
    ("Education", "expense", "📚", "#3b82f6"),
    ("Subscriptions", "expense", "💻", "#8b5cf6"),
    ("Fitness", "expense", "🏋️", "#10b981"),
]


@receiver(post_save, sender=User)
def seed_user_defaults(sender, instance, created, **kwargs):
    """When a user is created, seed default categories + assign USD as primary currency."""
    if not created:
        return

    # Default categories
    for name, type_, icon, color in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            user=instance, name=name, type=type_,
            defaults={"icon": icon, "color": color, "is_default": True}
        )

    # Default currency (NGN)
    ngn = Currency.objects.filter(code="NGN").first()
    if ngn:
        UserCurrency.objects.get_or_create(
            user=instance, currency=ngn,
            defaults={"is_primary": True}
        )