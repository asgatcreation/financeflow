from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal

from finance.models import (
    Category, Transaction, Budget, Currency, UserCurrency,
)
from .serializers import (
    UserSerializer, CurrencySerializer, UserCurrencySerializer,
    CategorySerializer, TransactionSerializer, BudgetSerializer,
)


# ═══════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════
class ObtainTokenView(APIView):
    """POST username + password → returns { token: "..." }"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data,
        })


class MeView(APIView):
    """GET the currently authenticated user."""
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ═══════════════════════════════════════════════════════════
# VIEWSETS
# ═══════════════════════════════════════════════════════════
class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """Global currency catalog (read-only)."""
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name"]
    pagination_class = None


class UserCurrencyViewSet(viewsets.ModelViewSet):
    """The currencies the current user tracks (max 5)."""
    serializer_class = UserCurrencySerializer
    search_fields = ["currency__code", "currency__name"]
    ordering_fields = ["created_at", "currency__code"]

    def get_queryset(self):
        return UserCurrency.objects.filter(user=self.request.user).select_related("currency")

    def perform_create(self, serializer):
        if UserCurrency.objects.filter(user=self.request.user).count() >= 5:
            raise permissions.exceptions.ValidationError("Max 5 currencies per user.")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # Block removal if transactions exist for that currency
        if Transaction.objects.filter(user=self.request.user, currency=instance.currency).exists():
            raise permissions.exceptions.ValidationError(
                "Can't remove this currency — it has transactions."
            )
        instance.delete()


class CategoryViewSet(viewsets.ModelViewSet):
    """Categories — user-scoped."""
    serializer_class = CategorySerializer
    search_fields = ["name"]
    ordering_fields = ["name", "type", "created_at"]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    """Transactions — user-scoped, filterable, searchable, orderable."""
    serializer_class = TransactionSerializer
    search_fields = ["description", "notes"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).select_related("category", "currency")

        # Filtering
        type_ = self.request.query_params.get("type")
        if type_ in ("income", "expense"):
            qs = qs.filter(type=type_)

        currency_code = self.request.query_params.get("currency")
        if currency_code:
            qs = qs.filter(currency__code=currency_code.upper())

        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)

        date_from = self.request.query_params.get("from")
        if date_from:
            qs = qs.filter(date__gte=date_from)

        date_to = self.request.query_params.get("to")
        if date_to:
            qs = qs.filter(date__lte=date_to)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """GET /api/transactions/summary/ — per-currency totals."""
        qs = self.get_queryset()
        agg = (
            qs.values("currency__code", "currency__symbol", "currency__flag", "type")
            .annotate(total=Sum("amount"))
        )
        by_currency = {}
        for row in agg:
            code = row["currency__code"] or "—"
            if code not in by_currency:
                by_currency[code] = {
                    "code": code,
                    "symbol": row["currency__symbol"] or "",
                    "flag": row["currency__flag"] or "",
                    "income": Decimal("0"),
                    "expense": Decimal("0"),
                }
            if row["type"] == "income":
                by_currency[code]["income"] += row["total"]
            else:
                by_currency[code]["expense"] += row["total"]

        results = []
        for v in by_currency.values():
            v["net"] = v["income"] - v["expense"]
            v["income"] = str(v["income"])
            v["expense"] = str(v["expense"])
            v["net"] = str(v["net"])
            results.append(v)
        return Response({"summary": results, "count": qs.count()})


class BudgetViewSet(viewsets.ModelViewSet):
    """Budgets — user-scoped."""
    serializer_class = BudgetSerializer
    search_fields = ["category__name"]
    ordering_fields = ["year", "month", "amount"]
    ordering = ["-year", "-month"]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related("category", "currency")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """GET /api/budgets/current/ — this month's budgets."""
        from django.utils import timezone
        now = timezone.now()
        qs = self.get_queryset().filter(month=now.month, year=now.year)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)