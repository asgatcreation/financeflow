from django import forms
from django.utils import timezone
from .models import Category, Transaction, Budget, Currency, UserCurrency


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type", "icon", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Groceries", "class": "form-input"}),
            "type": forms.Select(attrs={"class": "form-input"}),
            "icon": forms.Select(attrs={"class": "form-input"}),
            "color": forms.Select(attrs={"class": "form-input"}),
        }


class TransactionForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input"}),
        initial=timezone.now,
    )

    class Meta:
        model = Transaction
        fields = ["type", "amount", "currency", "category", "date", "description", "notes", "receipt"]
        widgets = {
            "type": forms.Select(attrs={"class": "form-input", "id": "id_type"}),
            "amount": forms.NumberInput(attrs={
                "class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00",
            }),
            "currency": forms.Select(attrs={"class": "form-input", "id": "id_currency"}),
            "category": forms.Select(attrs={"class": "form-input", "id": "id_category"}),
            "description": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "What was it for?",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-input", "rows": 3, "placeholder": "Optional notes...",
            }),
            "receipt": forms.FileInput(attrs={
                "class": "form-input",
                "accept": "image/*",
                "id": "id_receipt",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            # Only show categories belonging to the current user
            self.fields["category"].queryset = Category.objects.filter(user=user)
            self.fields["category"].required = False
            # Only show currencies the user has enabled
            user_currency_ids = list(
                UserCurrency.objects.filter(user=user).values_list("currency_id", flat=True)
            )
            self.fields["currency"].queryset = Currency.objects.filter(id__in=user_currency_ids)
            self.fields["currency"].required = True
            # Default to primary currency if creating new
            if not self.instance.pk:
                primary = UserCurrency.objects.filter(user=user, is_primary=True).first()
                if primary:
                    self.fields["currency"].initial = primary.currency

    def clean(self):
        cleaned = super().clean()
        type_ = cleaned.get("type")
        category = cleaned.get("category")
        amount = cleaned.get("amount")

        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")

        if category and type_ and category.type != type_:
            raise forms.ValidationError(
                f"Selected category is for {category.type}s, but you chose {type}."
            )
        return cleaned


class BudgetForm(forms.ModelForm):
    month = forms.ChoiceField(
        choices=[(i, f"{i:02d}") for i in range(1, 13)],
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Budget
        fields = ["category", "currency", "amount", "month", "year"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-input"}),
            "currency": forms.Select(attrs={"class": "form-input"}),
            "amount": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
            "year": forms.NumberInput(attrs={"class": "form-input", "min": "2020", "max": "2100"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user, type="expense")
            user_currency_ids = list(
                UserCurrency.objects.filter(user=user).values_list("currency_id", flat=True)
            )
            self.fields["currency"].queryset = Currency.objects.filter(id__in=user_currency_ids)
            self.fields["currency"].required = True
        self.fields["year"].initial = timezone.now().year
        self.fields["month"].initial = timezone.now().month


class UserCurrencyForm(forms.Form):
    """Add a new currency to the user's wallet."""
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-input"}),
        label="Add a currency",
    )
    is_primary = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        label="Set as primary currency",
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            # Exclude currencies the user already has
            owned = UserCurrency.objects.filter(user=user).values_list("currency_id", flat=True)
            self.fields["currency"].queryset = Currency.objects.filter(
                is_active=True
            ).exclude(id__in=owned)