from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ObtainTokenView, MeView,
    CurrencyViewSet, UserCurrencyViewSet,
    CategoryViewSet, TransactionViewSet, BudgetViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("currencies", CurrencyViewSet, basename="currency")
router.register("user-currencies", UserCurrencyViewSet, basename="user-currency")
router.register("categories", CategoryViewSet, basename="category")
router.register("transactions", TransactionViewSet, basename="transaction")
router.register("budgets", BudgetViewSet, basename="budget")

urlpatterns = [
    path("auth/token/", ObtainTokenView.as_view(), name="obtain-token"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]