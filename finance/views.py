import csv
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.utils import timezone

from .models import Category, Transaction, Budget, Currency, UserCurrency
from .forms import CategoryForm, TransactionForm, BudgetForm, UserCurrencyForm
from django.shortcuts import render


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def month_range(d):
    """Return (first_day, last_day) of the month containing d."""
    first = d.replace(day=1)
    if first.month == 12:
        last = first.replace(year=first.year + 1, month=1) - timedelta(days=1)
    else:
        last = first.replace(month=first.month + 1) - timedelta(days=1)
    return first, last


def monthly_series(user, months_back=6, currency=None):
    today = date.today()
    first_month = (today.replace(day=1) - timedelta(days=30 * (months_back - 1))).replace(day=1)

    qs = Transaction.objects.filter(user=user, date__gte=first_month)
    if currency is not None:
        qs = qs.filter(currency=currency)

    qs = (
        qs.annotate(month=TruncMonth("date"))
        .values("month", "type")
        .annotate(total=Sum("amount"))
    )

    by_month = {}
    for row in qs:
        key = row["month"].strftime("%Y-%m")
        by_month.setdefault(key, {"income": Decimal("0"), "expense": Decimal("0")})
        by_month[key][row["type"]] = row["total"]

    labels, income, expense = [], [], []
    cursor = first_month
    for _ in range(months_back):
        key = cursor.strftime("%Y-%m")
        row = by_month.get(key, {"income": Decimal("0"), "expense": Decimal("0")})
        labels.append(cursor.strftime("%b %Y"))
        income.append(float(row["income"]))
        expense.append(float(row["expense"]))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)
    return labels, income, expense


def category_breakdown(user, type_="expense", start=None, end=None, currency=None):
    qs = Transaction.objects.filter(user=user, type=type_)
    if currency is not None:
        qs = qs.filter(currency=currency)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    rows = (
        qs.values("category__name", "category__icon", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    labels, data, colors = [], [], []
    for row in rows:
        name = row["category__name"] or "Uncategorized"
        icon = row["category__icon"] or "💳"
        labels.append(f"{icon} {name}")
        data.append(float(row["total"]))
        colors.append(row["category__color"] or "#10b981")
    return labels, data, colors



# ─────────────────────────────────────────────────────────
# Landing
# ─────────────────────────────────────────────────────────
class LandingView(TemplateView):
    template_name = "finance/landing.html"


# ─────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "finance/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        first, last = month_range(today)

        # User's enabled currencies
        user_currencies = list(
            UserCurrency.objects.filter(user=user).select_related("currency")
        )
        user_currency_list = [uc.currency for uc in user_currencies]
        currency_ids = [c.id for c in user_currency_list]

        # If user has no currencies, no charts
        if not currency_ids:
            ctx.update({
                "user_currencies": [],
                "per_currency": [],
                "recent": [],
                "budgets": [],
                "now_month": today.strftime("%B %Y"),
                "chart_labels": json.dumps([]),
                "chart_income": json.dumps([]),
                "chart_expense": json.dumps([]),
                "cat_labels": json.dumps([]),
                "cat_data": json.dumps([]),
                "cat_colors": json.dumps([]),
                "no_currencies": True,
            })
            return ctx

        # ── Per-currency summary cards ──
        per_currency = []
        for c in user_currency_list:
            qs = Transaction.objects.filter(user=user, currency=c)
            month_qs = qs.filter(date__gte=first, date__lte=last)
            total_income = qs.filter(type="income").aggregate(t=Sum("amount"))["t"] or Decimal("0")
            total_expense = qs.filter(type="expense").aggregate(t=Sum("amount"))["t"] or Decimal("0")
            m_income = month_qs.filter(type="income").aggregate(t=Sum("amount"))["t"] or Decimal("0")
            m_expense = month_qs.filter(type="expense").aggregate(t=Sum("amount"))["t"] or Decimal("0")
            uc = next(x for x in user_currencies if x.currency_id == c.id)
            per_currency.append({
                "currency": c,
                "is_primary": uc.is_primary,
                "balance": total_income - total_expense,
                "total_income": total_income,
                "total_expense": total_expense,
                "m_income": m_income,
                "m_expense": m_expense,
                "m_net": m_income - m_expense,
            })

        # ── Charts use the primary currency only ──
        primary = next((x for x in per_currency if x["is_primary"]), per_currency[0])
        pc = primary["currency"]

        labels, income, expense = monthly_series(user, 6, currency=pc)
        cat_labels, cat_data, cat_colors = category_breakdown(user, "expense", first, last, currency=pc)

        recent = (
            Transaction.objects.filter(user=user, currency__in=currency_ids)
            .select_related("category", "currency")[:8]
        )
        budgets = (
            Budget.objects.filter(user=user, month=today.month, year=today.year)
            .select_related("category", "currency")
        )

        ctx.update({
            "user_currencies": user_currency_list,
            "per_currency": per_currency,
            "primary_currency": pc,
            "recent": recent,
            "budgets": budgets,
            "now_month": today.strftime("%B %Y"),
            "chart_labels": json.dumps(labels),
            "chart_income": json.dumps(income),
            "chart_expense": json.dumps(expense),
            "cat_labels": json.dumps(cat_labels),
            "cat_data": json.dumps(cat_data),
            "cat_colors": json.dumps(cat_colors),
            "no_currencies": False,
        })
        return ctx


class CurrenciesView(LoginRequiredMixin, View):
    """Manage the user's selected currencies (max 5)."""

    MAX_CURRENCIES = 5

    def get(self, request):
        user_currencies = UserCurrency.objects.filter(user=request.user).select_related("currency")
        form = UserCurrencyForm(user=request.user)
        return render(request, "finance/currencies.html", {
            "user_currencies": user_currencies,
            "form": form,
            "max_currencies": self.MAX_CURRENCIES,
        })

    def post(self, request):
        user_currencies = UserCurrency.objects.filter(user=request.user).select_related("currency")

        if user_currencies.count() >= self.MAX_CURRENCIES:
            messages.error(request, f"You can have at most {self.MAX_CURRENCIES} currencies.")
            return redirect("finance:currencies")

        form = UserCurrencyForm(request.POST, user=request.user)
        if form.is_valid():
            currency = form.cleaned_data["currency"]
            is_primary = form.cleaned_data["is_primary"]

            if is_primary:
                UserCurrency.objects.filter(user=request.user).update(is_primary=False)

            UserCurrency.objects.create(
                user=request.user,
                currency=currency,
                is_primary=is_primary or user_currencies.count() == 0,
            )
            messages.success(request, f"{currency.code} added to your wallet.")
            return redirect("finance:currencies")

        return render(request, "finance/currencies.html", {
            "user_currencies": user_currencies,
            "form": form,
            "max_currencies": self.MAX_CURRENCIES,
        })


class CurrencySetPrimaryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        uc = get_object_or_404(UserCurrency, pk=pk, user=request.user)
        UserCurrency.objects.filter(user=request.user).update(is_primary=False)
        uc.is_primary = True
        uc.save()
        messages.success(request, f"{uc.currency.code} is now your primary currency.")
        return redirect("finance:currencies")


class CurrencyRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        uc = get_object_or_404(UserCurrency, pk=pk, user=request.user)
        code = uc.currency.code
        # Prevent removing if there are transactions in it
        tx_count = Transaction.objects.filter(user=request.user, currency=uc.currency).count()
        if tx_count > 0:
            messages.error(
                request,
                f"Can't remove {code} — you have {tx_count} transaction(s) using it."
            )
            return redirect("finance:currencies")
        uc.delete()
        messages.success(request, f"{code} removed.")
        return redirect("finance:currencies")
# ─────────────────────────────────────────────────────────
# Transactions
# ─────────────────────────────────────────────────────────
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/transactions.html"
    context_object_name = "transactions"
    paginate_by = 15

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).select_related("category")

        q = self.request.GET.get("q", "").strip()
        type_ = self.request.GET.get("type", "")
        category_id = self.request.GET.get("category", "")
        start = self.request.GET.get("start", "")
        end = self.request.GET.get("end", "")

        if q:
            qs = qs.filter(Q(description__icontains=q) | Q(notes__icontains=q))
        if type_ in ("income", "expense"):
            qs = qs.filter(type=type_)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.filter(user=self.request.user)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["type"] = self.request.GET.get("type", "")
        ctx["category_id"] = self.request.GET.get("category", "")
        ctx["start"] = self.request.GET.get("start", "")
        ctx["end"] = self.request.GET.get("end", "")
        # totals for filtered set
        agg = self.get_queryset().aggregate(
            inc=Sum("amount", filter=Q(type="income")),
            exp=Sum("amount", filter=Q(type="expense")),
        )
        ctx["filtered_income"] = agg["inc"] or Decimal("0")
        ctx["filtered_expense"] = agg["exp"] or Decimal("0")
        return ctx


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transactions")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Transaction added.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "New Transaction"
        ctx["button_text"] = "Save Transaction"
        return ctx


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transactions")

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        messages.success(self.request, "Transaction updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit Transaction"
        ctx["button_text"] = "Save Changes"
        return ctx


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("finance:transactions")

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Transaction deleted.")
        return super().form_valid(form)


class ExportCSVView(LoginRequiredMixin, View):
    def get(self, request):
        qs = Transaction.objects.filter(user=request.user).select_related("category")
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(["Date", "Type", "Amount", "Category", "Description", "Notes"])
        for t in qs:
            writer.writerow([
                t.date, t.type, t.amount,
                t.category.name if t.category else "",
                t.description, t.notes,
            ])
        return response


# ─────────────────────────────────────────────────────────
# Categories
# ─────────────────────────────────────────────────────────
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "finance/categories.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:categories")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Category created.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "New Category"
        ctx["button_text"] = "Create Category"
        return ctx


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:categories")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit Category"
        ctx["button_text"] = "Save Changes"
        return ctx


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "finance/category_confirm_delete.html"
    success_url = reverse_lazy("finance:categories")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category deleted.")
        return super().form_valid(form)


# ─────────────────────────────────────────────────────────
# Budgets
# ─────────────────────────────────────────────────────────
class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = "finance/budgets.html"
    context_object_name = "budgets"

    def get_queryset(self):
        return (
            Budget.objects.filter(user=self.request.user)
            .select_related("category")
            .order_by("-year", "-month", "category__name")
        )


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "finance/budget_form.html"
    success_url = reverse_lazy("finance:budgets")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Budget set.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "New Budget"
        ctx["button_text"] = "Save Budget"
        return ctx


class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = "finance/budget_form.html"
    success_url = reverse_lazy("finance:budgets")

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit Budget"
        ctx["button_text"] = "Save Changes"
        return ctx


class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = "finance/budget_confirm_delete.html"
    success_url = reverse_lazy("finance:budgets")

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Budget deleted.")
        return super().form_valid(form)


# ─────────────────────────────────────────────────────────
# Reports
# ─────────────────────────────────────────────────────────
class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "finance/reports.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        first, last = month_range(today)

        user_currencies = list(UserCurrency.objects.filter(user=user).select_related("currency"))
        currency_list = [uc.currency for uc in user_currencies]

        if not currency_list:
            ctx["no_currencies"] = True
            ctx["user_currencies"] = []
            ctx["active_currency"] = None
            return ctx

        # Currency selector
        code = self.request.GET.get("currency", "").upper()
        active = next((c for c in currency_list if c.code == code), currency_list[0])

        labels, income, expense = monthly_series(user, 12, currency=active)
        cat_labels, cat_data, cat_colors = category_breakdown(user, "expense", first, last, currency=active)
        inc_labels, inc_data, inc_colors = category_breakdown(user, "income", first, last, currency=active)

        ctx.update({
            "user_currencies": currency_list,
            "active_currency": active,
            "chart_labels": json.dumps(labels),
            "chart_income": json.dumps(income),
            "chart_expense": json.dumps(expense),
            "cat_labels": json.dumps(cat_labels),
            "cat_data": json.dumps(cat_data),
            "cat_colors": json.dumps(cat_colors),
            "inc_labels": json.dumps(inc_labels),
            "inc_data": json.dumps(inc_data),
            "inc_colors": json.dumps(inc_colors),
            "now_month": today.strftime("%B %Y"),
            "no_currencies": False,
        })
        return ctx
