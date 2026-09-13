from django.db import migrations


CURRENCIES = [
    ("NGN", "Nigerian Naira", "₦", "🇳🇬"),
    ("USD", "US Dollar", "$", "🇺🇸"),
    ("EUR", "Euro", "€", "🇪🇺"),
    ("GBP", "British Pound", "£", "🇬🇧"),
    ("JPY", "Japanese Yen", "¥", "🇯🇵"),
    ("CAD", "Canadian Dollar", "C$", "🇨🇦"),
    ("AUD", "Australian Dollar", "A$", "🇦🇺"),
    ("INR", "Indian Rupee", "₹", "🇮🇳"),
    ("CNY", "Chinese Yuan", "¥", "🇨🇳"),
    ("ZAR", "South African Rand", "R", "🇿🇦"),
    ("GHS", "Ghanaian Cedi", "₵", "🇬🇭"),
    ("KES", "Kenyan Shilling", "KSh", "🇰🇪"),
    ("AED", "UAE Dirham", "د.إ", "🇦🇪"),
    ("SAR", "Saudi Riyal", "﷼", "🇸🇦"),
    ("CHF", "Swiss Franc", "Fr", "🇨🇭"),
    ("BRL", "Brazilian Real", "R$", "🇧🇷"),
    ("MXN", "Mexican Peso", "$", "🇲🇽"),
    ("SGD", "Singapore Dollar", "S$", "🇸🇬"),
    ("HKD", "Hong Kong Dollar", "HK$", "🇭🇰"),
    ("KRW", "South Korean Won", "₩", "🇰🇷"),
]


def seed_currencies(apps, schema_editor):
    Currency = apps.get_model("finance", "Currency")
    for code, name, symbol, flag in CURRENCIES:
        Currency.objects.get_or_create(
            code=code,
            defaults={"name": name, "symbol": symbol, "flag": flag, "is_active": True},
        )


def unseed_currencies(apps, schema_editor):
    Currency = apps.get_model("finance", "Currency")
    Currency.objects.filter(code__in=[c[0] for c in CURRENCIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0002_currency_category_is_default_alter_budget_amount_and_more"),
    ]
    operations = [migrations.RunPython(seed_currencies, unseed_currencies)]