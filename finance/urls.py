from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    # Landing
    path("", views.LandingView.as_view(), name="landing"),

    # Dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),

    # Transactions
    path("transactions/", views.TransactionListView.as_view(), name="transactions"),
    path("transactions/new/", views.TransactionCreateView.as_view(), name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.TransactionUpdateView.as_view(), name="transaction_update"),
    path("transactions/<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="transaction_delete"),
    path("transactions/export/", views.ExportCSVView.as_view(), name="transaction_export"),

    # Categories
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Budgets
    path("budgets/", views.BudgetListView.as_view(), name="budgets"),
    path("budgets/new/", views.BudgetCreateView.as_view(), name="budget_create"),
    path("budgets/<int:pk>/edit/", views.BudgetUpdateView.as_view(), name="budget_update"),
    path("budgets/<int:pk>/delete/", views.BudgetDeleteView.as_view(), name="budget_delete"),

    # Reports
    path("reports/", views.ReportsView.as_view(), name="reports"),
    
    # Currencies
    path("currencies/", views.CurrenciesView.as_view(), name="currencies"),
    path("currencies/<int:pk>/primary/", views.CurrencySetPrimaryView.as_view(), name="currency_primary"),
    path("currencies/<int:pk>/remove/", views.CurrencyRemoveView.as_view(), name="currency_remove"),
]