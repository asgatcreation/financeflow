from rest_framework import serializers
from django.contrib.auth.models import User
from finance.models import (
    Category, Transaction, Budget, Currency, UserCurrency,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = ["id", "username", "date_joined"]


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "code", "name", "symbol", "flag", "is_active"]


class UserCurrencySerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_code = serializers.CharField(write_only=True)

    class Meta:
        model = UserCurrency
        fields = ["id", "currency", "currency_code", "is_primary", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        code = validated_data.pop("currency_code").upper()
        try:
            currency = Currency.objects.get(code=code)
        except Currency.DoesNotExist:
            raise serializers.ValidationError({"currency_code": f"Currency '{code}' not found."})
        user = self.context["request"].user
        if UserCurrency.objects.filter(user=user, currency=currency).exists():
            raise serializers.ValidationError({"currency_code": "You already track this currency."})
        return UserCurrency.objects.create(user=user, currency=currency, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("currency_code", None)
        if validated_data.get("is_primary"):
            UserCurrency.objects.filter(user=instance.user).update(is_primary=False)
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    transaction_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "type", "type_display",
            "icon", "color", "is_default",
            "transaction_count", "created_at",
        ]
        read_only_fields = ["id", "is_default", "created_at"]

    def get_transaction_count(self, obj):
        return obj.transactions.count()


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)
    category_color = serializers.CharField(source="category.color", read_only=True)
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    currency_symbol = serializers.CharField(source="currency.symbol", read_only=True)
    currency_flag = serializers.CharField(source="currency.flag", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id", "type", "amount",
            "category", "category_name", "category_icon", "category_color",
            "currency", "currency_code", "currency_symbol", "currency_flag",
            "date", "description", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        # Category must belong to the user
        request = self.context["request"]
        category = data.get("category")
        if category and category.user_id != request.user.id:
            raise serializers.ValidationError({"category": "Not your category."})

        # Category type must match transaction type
        type_ = data.get("type")
        if category and type_ and category.type != type_:
            raise serializers.ValidationError({
                "category": f"Category is for {category.type}s but you chose {type_}."
            })
        return data


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    currency_symbol = serializers.CharField(source="currency.symbol", read_only=True)
    spent = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    percent_used = serializers.IntegerField(read_only=True)
    is_over = serializers.BooleanField(read_only=True)
    is_warning = serializers.BooleanField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "category", "category_name", "category_icon",
            "currency", "currency_code", "currency_symbol",
            "amount", "month", "year",
            "spent", "remaining", "percent_used", "is_over", "is_warning",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        return value

    def validate_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value