from django.contrib import admin
from .models import Category, Transaction, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "icon", "user", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("name", "user__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("description", "type", "amount", "category", "date", "user")
    list_filter = ("type", "date", "category")
    search_fields = ("description", "notes", "user__username")
    date_hierarchy = "date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("category", "amount", "month", "year", "user")
    list_filter = ("year", "month", "category")
    search_fields = ("category__name", "user__username")

from .models import Currency, UserCurrency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "flag", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(UserCurrency)
class UserCurrencyAdmin(admin.ModelAdmin):
    list_display = ("user", "currency", "is_primary", "created_at")
    list_filter = ("is_primary", "currency")
    search_fields = ("user__username", "currency__code")
    
from .models import RecurringTransaction

@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ("description", "user", "type", "amount", "currency", "frequency", "next_run_datetime", "is_active")
    list_filter = ("frequency", "is_active", "type", "currency")
    search_fields = ("description", "user__username")
    list_editable = ("is_active",)
    date_hierarchy = "next_run_datetime"    
    
    