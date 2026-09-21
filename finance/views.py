import csv
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.utils import timezone

from .models import Category, Transaction, Budget, Currency, UserCurrency
from .forms import CategoryForm, TransactionForm, BudgetForm, UserCurrencyForm
from django.shortcuts import render
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


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

def apply_transaction_filters(qs, request):
    """Apply the same filter query params used on the transactions list."""
    q = request.GET.get("q", "").strip()
    type_ = request.GET.get("type", "")
    category_id = request.GET.get("category", "")
    currency_code = request.GET.get("currency", "")
    start = request.GET.get("start", "")
    end = request.GET.get("end", "")

    if q:
        qs = qs.filter(Q(description__icontains=q) | Q(notes__icontains=q))
    if type_ in ("income", "expense"):
        qs = qs.filter(type=type_)
    if category_id:
        qs = qs.filter(category_id=category_id)
    if currency_code:
        qs = qs.filter(currency__code=currency_code)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    return qs


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

        user_currencies = list(
            UserCurrency.objects.filter(user=user).select_related("currency")
        )
        user_currency_list = [uc.currency for uc in user_currencies]
        currency_ids = [c.id for c in user_currency_list]

        if not currency_ids:
            ctx.update({
                "user_currencies": [], "per_currency": [], "recent": [],
                "budgets": [], "now_month": today.strftime("%B %Y"),
                "chart_labels": json.dumps([]),
                "chart_income": json.dumps([]),
                "chart_expense": json.dumps([]),
                "cat_labels": json.dumps([]), "cat_data": json.dumps([]),
                "cat_colors": json.dumps([]),
                "all_currency_series": json.dumps([]),
                "no_currencies": True,
            })
            return ctx

        # Per-currency summary
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

        # Charts use primary or ?chart=CODE
        chart_code = self.request.GET.get("chart", "").upper()
        pc = next((c for c in user_currency_list if c.code == chart_code), None)
        if not pc:
            pc = next((x["currency"] for x in per_currency if x["is_primary"]), user_currency_list[0])

        labels, income, expense = monthly_series(user, 6, currency=pc)
        cat_labels, cat_data, cat_colors = category_breakdown(user, "expense", first, last, currency=pc)
        inc_cat_labels, inc_cat_data, inc_cat_colors = category_breakdown(user, "income", first, last, currency=pc)

        # ── All-currency series (normalized to primary using rough FX or raw) ──
        all_currency_series = []
        palette = ["#10b981", "#0ea5e9", "#8b5cf6", "#f59e0b", "#f43f5e"]
        for i, c in enumerate(user_currency_list):
            _, c_income, c_expense = monthly_series(user, 6, currency=c)
            c_net = [a - b for a, b in zip(c_income, c_expense)]
            all_currency_series.append({
                "code": c.code,
                "flag": c.flag,
                "color": palette[i % len(palette)],
                "net_series": c_net,
            })

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
            "inc_cat_labels": json.dumps(inc_cat_labels),
            "inc_cat_data": json.dumps(inc_cat_data),
            "inc_cat_colors": json.dumps(inc_cat_colors),
            "chart_currency": pc,
            "all_currency_series": json.dumps(all_currency_series),
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
        qs = (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related("category", "currency")
        )
        qs = apply_transaction_filters(qs, self.request)

        sort = self.request.GET.get("sort", "newest")
        sort_map = {
            "newest": "-date",
            "oldest": "date",
            "highest": "-amount",
            "lowest": "amount",
        }
        return qs.order_by(sort_map.get(sort, "-date"))
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["categories"] = Category.objects.filter(user=user)
        ctx["user_currencies"] = UserCurrency.objects.filter(user=user).select_related("currency")

        ctx["q"] = self.request.GET.get("q", "")
        ctx["type"] = self.request.GET.get("type", "")
        ctx["category_id"] = self.request.GET.get("category", "")
        ctx["currency_code"] = self.request.GET.get("currency", "")
        ctx["start"] = self.request.GET.get("start", "")
        ctx["end"] = self.request.GET.get("end", "")
        ctx["sort"] = self.request.GET.get("sort", "newest")

        agg = (
            self.get_queryset()
            .values("currency__code", "currency__symbol", "currency__flag", "currency__name", "type")
            .annotate(total=Sum("amount"))
            .order_by("currency__code")
        )
        by_currency = {}
        for row in agg:
            code = row["currency__code"] or "—"
            if code not in by_currency:
                by_currency[code] = {
                    "code": code, "symbol": row["currency__symbol"] or "",
                    "flag": row["currency__flag"] or "🏳️",
                    "name": row["currency__name"] or "Unknown",
                    "income": Decimal("0"), "expense": Decimal("0"),
                }
            if row["type"] == "income":
                by_currency[code]["income"] += row["total"]
            else:
                by_currency[code]["expense"] += row["total"]
        for v in by_currency.values():
            v["net"] = v["income"] - v["expense"]
        ctx["currency_totals"] = sorted(by_currency.values(), key=lambda x: -(x["income"] + x["expense"]))
        return ctx





class CurrencyDetailView(LoginRequiredMixin, TemplateView):
    template_name = "finance/currency_detail.html"
    PER_PAGE = 10

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.kwargs["code"].upper()
        user = self.request.user

        try:
            currency = Currency.objects.get(code=code)
        except Currency.DoesNotExist:
            ctx["not_found"] = True
            return ctx

        if not UserCurrency.objects.filter(user=user, currency=currency).exists():
            ctx["not_found"] = True
            return ctx

        qs = (
            Transaction.objects.filter(user=user, currency=currency)
            .select_related("category")
        )

        sort = self.request.GET.get("sort", "newest")
        sort_map = {
            "newest": "-date",
            "oldest": "date",
            "highest": "-amount",
            "lowest": "amount",
            "category": "category__name",
        }
        qs = qs.order_by(sort_map.get(sort, "-date"))

        income = qs.filter(type="income").aggregate(t=Sum("amount"))["t"] or Decimal("0")
        expense = qs.filter(type="expense").aggregate(t=Sum("amount"))["t"] or Decimal("0")
        net = income - expense

        cat_breakdown = (
            qs.filter(type="expense")
            .values("category__name", "category__icon", "category__color")
            .annotate(total=Sum("amount"))
            .order_by("-total")[:8]
        )

        # ── Pagination ──
        from django.core.paginator import Paginator
        paginator = Paginator(qs, self.PER_PAGE)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        ctx.update({
            "currency": currency,
            "transactions": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "income": income,
            "expense": expense,
            "net": net,
            "count": paginator.count,
            "sort": sort,
            "cat_breakdown": cat_breakdown,
            "not_found": False,
        })
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
        ctx["all_categories"] = Category.objects.filter(user=self.request.user).order_by("type", "name")
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
        ctx["all_categories"] = Category.objects.filter(user=self.request.user).order_by("type", "name")
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
        qs = (
            Transaction.objects.filter(user=request.user)
            .select_related("category", "currency")
            .order_by("-date")
        )
        qs = apply_transaction_filters(qs, request)

        response = HttpResponse(content_type="text/csv")
        filename = f"financeflow_transactions_{date.today().isoformat()}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "Date", "Type", "Amount", "Currency Code", "Currency Symbol",
            "Category", "Description", "Notes", "Created At",
        ])
        for t in qs:
            writer.writerow([
                t.date.isoformat() if t.date else "",
                t.type.capitalize(),
                f"{t.amount:.2f}",
                t.currency.code if t.currency else "",
                t.currency.symbol if t.currency else "",
                t.category.name if t.category else "Uncategorized",
                t.description,
                t.notes or "",
                t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "",
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

        user_currencies = list(
            UserCurrency.objects.filter(user=user).select_related("currency")
        )
        currency_list = [uc.currency for uc in user_currencies]

        if not currency_list:
            ctx["no_currencies"] = True
            ctx["user_currencies"] = []
            ctx["active_currency"] = None
            ctx["per_currency"] = []
            ctx["all_currency_series"] = json.dumps([])
            ctx["per_currency_json"] = json.dumps([])
            return ctx

        code = self.request.GET.get("currency", "").upper()
        active = next((c for c in currency_list if c.code == code), currency_list[0])

        labels, income, expense = monthly_series(user, 12, currency=active)
        cat_labels, cat_data, cat_colors = category_breakdown(user, "expense", first, last, currency=active)
        inc_labels, inc_data, inc_colors = category_breakdown(user, "income", first, last, currency=active)

        # ── Predictions ──
        income_nonzero = [x for x in income if x > 0]
        expense_nonzero = [x for x in expense if x > 0]

        def weighted_avg(series, weights=(0.5, 0.3, 0.2)):
            if len(series) < len(weights):
                return sum(series) / len(series) if series else 0
            recent = series[-len(weights):]
            return sum(v * w for v, w in zip(reversed(recent), weights))

        pred_income = weighted_avg(income_nonzero) if income_nonzero else 0
        pred_expense = weighted_avg(expense_nonzero) if expense_nonzero else 0
        pred_net = pred_income - pred_expense

        # ── Insights ──
        current_income = income[-1] if income else 0
        current_expense = expense[-1] if expense else 0
        prev_income = income[-2] if len(income) > 1 else 0
        prev_expense = expense[-2] if len(expense) > 1 else 0

        income_delta = ((current_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
        expense_delta = ((current_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0

        top_cat_label = cat_labels[0] if cat_labels else "—"
        top_cat_amount = cat_data[0] if cat_data else 0

        savings_rate = ((current_income - current_expense) / current_income * 100) if current_income > 0 else 0
        avg_expense = sum(expense) / len([e for e in expense if e > 0]) if any(e > 0 for e in expense) else 0
        avg_income = sum(income) / len([i for i in income if i > 0]) if any(i > 0 for i in income) else 0

        # ── Per-currency totals ──
        per_currency = []
        for c in currency_list:
            qs = Transaction.objects.filter(user=user, currency=c)
            ti = qs.filter(type="income").aggregate(t=Sum("amount"))["t"] or Decimal("0")
            te = qs.filter(type="expense").aggregate(t=Sum("amount"))["t"] or Decimal("0")
            per_currency.append({
                "currency": c,
                "total_income": ti,
                "total_expense": te,
                "balance": ti - te,
            })

        # ── All-currency net series (last 6 months) ──
        all_currency_series = []
        palette = ["#10b981", "#0ea5e9", "#8b5cf6", "#f59e0b", "#f43f5e"]
        for i, c in enumerate(currency_list):
            _, ci, ce = monthly_series(user, 6, currency=c)
            cn = [a - b for a, b in zip(ci, ce)]
            all_currency_series.append({
                "code": c.code,
                "flag": c.flag,
                "color": palette[i % len(palette)],
                "net_series": cn,
            })

        ctx.update({
            "user_currencies": currency_list,
            "active_currency": active,
            "per_currency": per_currency,
            "all_currency_series": json.dumps(all_currency_series),
            "per_currency_json": json.dumps([
                {
                    "flag": row["currency"].flag,
                    "code": row["currency"].code,
                    "symbol": row["currency"].symbol,
                    "income": float(row["total_income"]),
                    "expense": float(row["total_expense"]),
                    "net": float(row["balance"]),
                }
                for row in per_currency
            ]),
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
            "today": today,
            "no_currencies": False,
            "pred_income": pred_income,
            "pred_expense": pred_expense,
            "pred_net": pred_net,
            "pred_month": (today.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%B %Y"),
            "current_income": current_income,
            "current_expense": current_expense,
            "income_delta": income_delta,
            "expense_delta": expense_delta,
            "top_cat_label": top_cat_label,
            "top_cat_amount": top_cat_amount,
            "savings_rate": savings_rate,
            "avg_expense": avg_expense,
            "avg_income": avg_income,
        })
        return ctx



class ExportExcelView(LoginRequiredMixin, View):
    """Export all user transactions as a formatted .xlsx file."""

    def get(self, request):
        wb = Workbook()

        # ── Sheet 1: All Transactions ──
        ws = wb.active
        ws.title = "Transactions"

        # Header row styling
        header_fill = PatternFill("solid", fgColor="10b981")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style="thin", color="e2e8f0"),
            right=Side(style="thin", color="e2e8f0"),
            top=Side(style="thin", color="e2e8f0"),
            bottom=Side(style="thin", color="e2e8f0"),
        )

        headers = [
            "Date", "Type", "Amount", "Currency",
            "Symbol", "Category", "Description", "Notes",
        ]
        ws.append(headers)
        for col_num, _ in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border

        # Fetch transactions (respect current filters)
        qs = (
            Transaction.objects.filter(user=request.user)
            .select_related("category", "currency")
            .order_by("-date")
        )
        qs = apply_transaction_filters(qs, request)

        income_fill = PatternFill("solid", fgColor="ecfdf5")
        expense_fill = PatternFill("solid", fgColor="fff1f2")

        for t in qs:
            row = [
                t.date.isoformat() if t.date else "",
                t.type.capitalize(),
                float(t.amount),
                t.currency.code if t.currency else "",
                t.currency.symbol if t.currency else "",
                t.category.name if t.category else "Uncategorized",
                t.description,
                t.notes or "",
            ]
            ws.append(row)

            # Color the row by type
            current_row = ws.max_row
            fill = income_fill if t.type == "income" else expense_fill
            for col_num in range(1, len(headers) + 1):
                cell = ws.cell(row=current_row, column=col_num)
                cell.fill = fill
                cell.border = thin_border

        # Column widths
        widths = [12, 10, 14, 10, 8, 18, 40, 40]
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[chr(64 + i)].width = w

        # Freeze header
        ws.freeze_panes = "A2"

        # ── Sheet 2: Per-Currency Summary ──
        ws2 = wb.create_sheet("Summary by Currency")
        ws2.append(["Currency", "Symbol", "Total Income", "Total Expense", "Net"])
        for col_num in range(1, 6):
            cell = ws2.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border

        from django.db.models import Sum as _Sum
        agg = (
            qs.values("currency__code", "currency__symbol", "currency__flag", "type")
            .annotate(total=_Sum("amount"))
        )
        by_currency = {}
        for row in agg:
            code = row["currency__code"] or "—"
            if code not in by_currency:
                by_currency[code] = {
                    "symbol": row["currency__symbol"] or "",
                    "income": 0, "expense": 0,
                }
            if row["type"] == "income":
                by_currency[code]["income"] = float(row["total"])
            else:
                by_currency[code]["expense"] = float(row["total"])

        for code, data in sorted(by_currency.items()):
            net = data["income"] - data["expense"]
            ws2.append([code, data["symbol"], data["income"], data["expense"], net])
            r = ws2.max_row
            for c in range(1, 6):
                ws2.cell(row=r, column=c).border = thin_border

        for i, w in enumerate([12, 10, 16, 16, 16], 1):
            ws2.column_dimensions[chr(64 + i)].width = w

        # ── Sheet 3: Monthly Totals ──
        ws3 = wb.create_sheet("Monthly Totals")
        ws3.append(["Month", "Income", "Expense", "Net"])
        for col_num in range(1, 5):
            cell = ws3.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border

        from django.db.models.functions import TruncMonth
        monthly = (
            qs.annotate(month=TruncMonth("date"))
            .values("month", "type")
            .annotate(total=_Sum("amount"))
            .order_by("month")
        )
        by_month = {}
        for row in monthly:
            key = row["month"].strftime("%Y-%m") if row["month"] else "—"
            by_month.setdefault(key, {"income": 0, "expense": 0})
            by_month[key][row["type"]] = float(row["total"])

        for month_key in sorted(by_month.keys()):
            data = by_month[month_key]
            net = data["income"] - data["expense"]
            ws3.append([month_key, data["income"], data["expense"], net])
            r = ws3.max_row
            for c in range(1, 5):
                ws3.cell(row=r, column=c).border = thin_border

        for i, w in enumerate([14, 16, 16, 16], 1):
            ws3.column_dimensions[chr(64 + i)].width = w

        # ── Send the file ──
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"financeflow_{date.today().isoformat()}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response
    
    
    
    
    
from .forms import BulkTransactionFormSet


class BulkTransactionView(LoginRequiredMixin, View):
    """Add many transactions at once via a table."""
    template_name = "finance/transaction_bulk.html"

    def _ctx(self, request, formset):
        return {
            "formset": formset,
            "user_currencies": (
                UserCurrency.objects
                .filter(user=request.user)
                .select_related("currency")
                .order_by("-is_primary", "currency__code")
            ),
            "all_categories": Category.objects.filter(user=request.user).order_by("type", "name"),
        }

    def get(self, request):
        formset = BulkTransactionFormSet(user=request.user)
        return render(request, self.template_name, self._ctx(request, formset))

    def post(self, request):
        formset = BulkTransactionFormSet(request.POST, request.FILES, user=request.user)
        if formset.is_valid():
            created = 0
            for form in formset:
                if form.cleaned_data.get("DELETE"):
                    continue
                if not form.cleaned_data.get("amount"):
                    continue
                if not form.cleaned_data.get("description"):
                    continue
                instance = form.save(commit=False)
                instance.user = request.user
                # Handle receipt upload
                if form.cleaned_data.get("receipt"):
                    instance.receipt = form.cleaned_data["receipt"]
                instance.save()
                created += 1

            if created:
                messages.success(
                    request,
                    f"✅ {created} transaction{'s' if created != 1 else ''} added.",
                )
                return redirect("finance:transactions")
            else:
                messages.warning(request, "No transactions were added.")

        return render(request, self.template_name, self._ctx(request, formset))

