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
            

# ═══════════════════════════════════════════════════════════
# BULK ENTRY FORMSET
# ═══════════════════════════════════════════════════════════
from django.forms import BaseFormSet, formset_factory


class BulkTransactionForm(forms.ModelForm):
    """One row in the bulk-entry table. All fields optional so empty rows validate."""
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "bulk-input"}),
    )

    class Meta:
        model = Transaction
        fields = ["type", "amount", "currency", "category", "date", "description", "receipt"]
        widgets = {
            "type": forms.Select(attrs={"class": "bulk-input bulk-type"}),
            "amount": forms.NumberInput(attrs={
                "class": "bulk-input", "step": "0.01", "min": "0",
                "placeholder": "0.00", "inputmode": "decimal",
            }),
            "currency": forms.Select(attrs={"class": "bulk-input"}),
            "category": forms.Select(attrs={"class": "bulk-input"}),
            "description": forms.TextInput(attrs={
                "class": "bulk-input", "placeholder": "Description",
            }),
            "receipt": forms.FileInput(attrs={
                "accept": "image/*",
                "class": "fx-file-input",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Make everything optional at the form level so blank rows validate
        for name in self.fields:
            self.fields[name].required = False

        self.user = user
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user)
            uc_ids = UserCurrency.objects.filter(user=user).values_list("currency_id", flat=True)
            self.fields["currency"].queryset = Currency.objects.filter(id__in=uc_ids)

            # Sensible defaults for new rows
            if not self.is_bound and not self.instance.pk:
                primary = UserCurrency.objects.filter(user=user, is_primary=True).first()
                if primary:
                    self.fields["currency"].initial = primary.currency_id
                self.fields["date"].initial = timezone.now().date()

            # Put "Expense" first — most common
            self.fields["type"].choices = [("expense", "Expense"), ("income", "Income")]

    def clean(self):
        cleaned = super().clean()

        # A row is "blank" if none of the meaningful fields are filled
        has_content = bool(
            cleaned.get("amount") or
            cleaned.get("description") or
            cleaned.get("type") or
            cleaned.get("category")
        )
        if not has_content:
            return cleaned

        errors = []
        if not cleaned.get("type"):
            errors.append("Type is required.")
        if not cleaned.get("amount"):
            errors.append("Amount is required.")
        if not cleaned.get("description"):
            errors.append("Description is required.")
        if not cleaned.get("currency"):
            errors.append("Currency is required.")
        if errors:
            raise forms.ValidationError(errors)

        if cleaned["amount"] <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")

        cat = cleaned.get("category")
        if cat and cat.type != cleaned.get("type"):
            raise forms.ValidationError(
                f"Category '{cat.name}' is for {cat.type}s, but you chose {cleaned['type']}."
            )
        return cleaned


class BaseBulkTransactionFormSet(BaseFormSet):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def get_form_kwargs(self, index):
        kw = super().get_form_kwargs(index)
        kw["user"] = self.user
        return kw

    def clean(self):
        super().clean()
        # Require at least one filled-in row
        has_any = any(
            form.has_changed() and form.cleaned_data and form.cleaned_data.get("amount")
            for form in self.forms
        )
        if not has_any:
            raise forms.ValidationError("Add at least one transaction.")


BulkTransactionFormSet = formset_factory(
    BulkTransactionForm,
    formset=BaseBulkTransactionFormSet,
    extra=5,
    max_num=30,
    can_delete=True,
    validate_max=True,
)