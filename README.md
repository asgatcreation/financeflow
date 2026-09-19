<div align="center">

<br/>

# 💰 FinanceFlow

### Your money. All of it. In one place.

A modern, production-ready **multi-currency expense tracker and finance dashboard** built with Django 5, PostgreSQL, and Google OAuth.

<br/>

[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google OAuth](https://img.shields.io/badge/Google_OAuth-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/identity)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![Supabase](https://img.shields.io/badge/DB-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

[**🚀 Live Demo**](https://financeflow-app-uuu8.onrender.com) · [**🐛 Report Bug**](../../issues) · [**✨ Request Feature**](../../issues)

> ⚠️ Hosted on Render's free tier — the first load may take ~30 seconds while the app wakes up.

<br/>

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Screenshots](#-screenshots)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Google OAuth Setup](#-google-oauth-setup)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🎯 About

**FinanceFlow** is a fully-featured personal finance tracker built to solve a real problem: **managing money across multiple currencies without the headache of constant conversion.**

You can track Naira, Dollar, Euro, GBP, JPY, and 15 other currencies — **each transaction stays in its own currency**. Budgets, charts, and reports keep you in control. Built from scratch with Django 5, styled with a modern fintech UI, and deployed with production-grade tooling (PostgreSQL on Supabase, Gunicorn, Whitenoise, Google OAuth).

It's a showcase of **full-stack Django**: authentication, per-user data isolation, complex queries, aggregation, Chart.js integration, PDF export, predictive insights, custom admin, and cloud deployment.

### 🎬 What It Does

```
📝 Sign up  →  💱 Pick your currencies  →  💸 Log transactions
              ↓
📊 Watch charts update  →  🎯 Stay under budget  →  📥 Export anytime
```

---

## 📸 Screenshots

### 🌄 Landing Page
![Landing Page](docs/screenshots/01-landing.png)

### 🔐 Authentication
<table>
<tr>
<td width="50%" align="center">

**Login — split-screen with rotating slides**
![Login](docs/screenshots/02-login.png)

</td>
<td width="50%" align="center">

**Sign up — Google OAuth ready**
![Signup](docs/screenshots/03-signup.png)

</td>
</tr>
</table>

### 📊 Dashboard — Multi-Currency Overview
![Dashboard](docs/screenshots/04-dashboard.png)

### 💸 Transactions — Per-Currency Totals, Live Filters
![Transactions](docs/screenshots/05-transactions.png)

### 🔍 Currency Deep Dive — Filter, Sort, Paginate
![Currency Detail](docs/screenshots/05b-currency-detail.png)

### 🎯 Budgets — Per-Category, Per-Currency Limits
![Budgets](docs/screenshots/06-budgets.png)

### 📈 Reports — 12-Month Trends, Insights, PDF Export
![Reports](docs/screenshots/07-reports.png)

### 💱 Multi-Currency Wallet
<table>
<tr>
<td width="50%" align="center">

**Currencies — up to 5 per user**
![Currencies](docs/screenshots/08-currencies.png)

</td>
<td width="50%" align="center">

**Categories — 15+ pre-seeded**
![Categories](docs/screenshots/09-categories.png)

</td>
</tr>
</table>

### 📝 Transaction Form — Currency-Aware
![Transaction Form](docs/screenshots/10-transaction-form.png)

### 🛡️ Admin Console
<table>
<tr>
<td width="50%" align="center">

**Admin Login — split screen**
![Admin Login](docs/screenshots/11-admin-login.png)

</td>
<td width="50%" align="center">

**Admin Dashboard — sidebar navigation**
![Admin Dashboard](docs/screenshots/12-admin-dashboard.png)

</td>
</tr>
</table>

### 📱 Mobile Responsive
<table>
<tr>
<td width="33%" align="center">

**Mobile Landing**
![Mobile Landing](docs/screenshots/13-mobile-landing.png)

</td>
<td width="33%" align="center">

**Mobile Dashboard**
![Mobile Dashboard](docs/screenshots/14-mobile-dashboard.png)

</td>
<td width="33%" align="center">

**Mobile Admin**
![Mobile Admin](docs/screenshots/15-mobile-admin.png)

</td>
</tr>
</table>

---

## ✨ Features

### 💱 Multi-Currency Core
- Run up to **5 currencies simultaneously** per user
- Each transaction is stored in its own currency — no forced conversions
- **Per-currency totals on transactions** — no more mixed sums
- Per-currency **KPI cards** on the dashboard
- **20 currencies seeded** out of the box: 🇳🇬 NGN · 🇺🇸 USD · 🇪🇺 EUR · 🇬🇧 GBP · 🇯🇵 JPY · 🇨🇦 CAD · 🇦🇺 AUD · 🇮🇳 INR · 🇨🇳 CNY · 🇿🇦 ZAR · 🇬🇭 GHS · 🇰🇪 KES · 🇦🇪 AED · 🇸🇦 SAR · 🇨🇭 CHF · 🇧🇷 BRL · 🇲🇽 MXN · 🇸🇬 SGD · 🇭🇰 HKD · 🇰🇷 KRW
- Mark any currency as **primary** with a one-click star
- Remove currencies safely — blocked if transactions exist

### 🔐 Authentication
- **Email/password** registration with server-side validation
- **Google OAuth** via `django-allauth`
- Split-screen login/signup with **rotating slides**
- **Modal-based logout** confirmation — never a jarring redirect
- Password reset flow (forgot password)
- **Per-user data isolation** — you only see your own data, ever

### 📊 Dashboard
- **Hero welcome** with live overview
- **Per-currency KPI cards** — balance, monthly income, monthly expense, savings rate
- **4 interactive Chart.js charts** — 6-month trend, expense donut, income donut, savings bar
- **Currency selector** — switch all charts between your currencies
- Recent transactions feed
- Monthly budget progress inline
- **Skeleton loaders** for smoother perceived performance

### 💸 Transactions
- Full CRUD with inline validation
- **Per-currency totals row** — see NGN + USD + EUR side-by-side, never blended
- **Clear "Net" definition** — Net = Income − Expense for that specific currency
- **Live filter feedback** — search, type, category, date range
- **CSV export with full currency data** — UTF-8 BOM for Excel compatibility
- **Excel (.xlsx) export** — 3 sheets: transactions, per-currency summary, monthly totals
- Pagination (15 per page)
- Modern card-style rows with category icons, currency flags

### 🎯 Budgets
- Set monthly limits per category + per currency
- **Radial progress** visual per budget
- **Color states**: Emerald (safe), Amber (80–100%), Red (over)
- Category icon + currency flag shown inline
- Dashboard shows current-month budgets at a glance

### 📈 Reports
- **12-month bar chart** — income vs expense side by side
- **Category donuts** — expense and income breakdowns
- **Currency selector** — filter entire report by a single currency
- **6-month predictions** using weighted moving average
- **Insights card** — top spending category, biggest change, savings trend
- **Month-over-month deltas** — colored up/down arrows
- **PDF export** — one-click download of the full report
- Fully interactive (hover for values)

### 🏷️ Categories
- **15 pre-seeded categories** on signup: 💰 Salary · 💻 Freelance · 📈 Investments · 🎁 Gifts · 🛒 Groceries · 🏠 Rent · 🚗 Transport · 🍽️ Dining · 💡 Utilities · 💊 Healthcare · 🎬 Entertainment · 🛍️ Shopping · 📚 Education · 💻 Subscriptions · 🏋️ Fitness
- **21 icon choices** with labels
- **11 color options** for visual distinction in charts
- Fully editable / deletable per user

### 🛡️ Custom Admin Console
- **Sidebar navigation** (260px, collapsible on mobile)
- **Quick Action tiles** — Add user, Transactions, Social apps, Currencies
- **Model cards** with icons, descriptions, and dual actions
- **Custom split-screen admin login** — dark green gradient brand panel
- **Recent activity feed**
- **Mobile hamburger menu** with slide-in sidebar

### 🎨 Design System
- **Plus Jakarta Sans** typography
- **Emerald primary** (#10b981) + rose accents
- **Light, airy surfaces** with subtle shadows
- **Zero build step** — plain CSS, no Tailwind, no Webpack
- **Responsive** — mobile-first, sidebar collapses at 900px
- **Page-load animation** on every page
- **Chart.js defaults** — themed tooltips, grid colors, fonts

---

## 🧰 Tech Stack

<table>
<tr>
<td valign="top" width="25%">

**Backend**
- Django 5.0.6
- Python 3.12
- PostgreSQL 16 (Supabase)
- Gunicorn 22
- psycopg2-binary
- `dj-database-url`
- `python-dotenv`

</td>
<td valign="top" width="25%">

**Auth & Security**
- `django-allauth` 0.61
- Google OAuth 2.0
- CSRF + SSL redirect
- HSTS (1 year, preload)
- Secure cookies
- `X-Content-Type-Options: nosniff`

</td>
<td valign="top" width="25%">

**Frontend**
- Chart.js 4.4
- Plus Jakarta Sans
- Vanilla JS (carousel, modals, mobile menu, page loader, print)
- CSS custom properties
- Grid + Flexbox

</td>
<td valign="top" width="25%">

**Infra**
- Render (hosting)
- Supabase (PostgreSQL)
- Whitenoise (static files)
- GitHub (source + CI/CD)

</td>
</tr>
</table>

---

## 🏗️ Architecture

### Project Layout

```
financeflow/
├── accounts/                    # User app
├── finance/                     # Core finance app
│   ├── models.py                # Category, Transaction, Budget, Currency, UserCurrency
│   ├── forms.py
│   ├── views.py                 # Dashboard, CRUD, Reports, Currencies
│   ├── urls.py
│   ├── admin.py
│   ├── utils.py                 # Aggregation + prediction helpers
│   └── migrations/
├── expense_tracker/             # Project config
├── templates/
│   ├── account/                 # allauth templates
│   ├── admin/                   # Custom admin overrides
│   ├── finance/
│   ├── base.html                # Public layout
│   └── base_app.html            # Logged-in layout
├── static/css/style.css         # Full design system
├── docs/screenshots/            # README images
├── build.sh
├── render.yaml
└── manage.py
```

### Data Model

```
User (Django)
 ├─ 1:N → UserCurrency ── N:1 → Currency (global catalog)
 ├─ 1:N → Category
 ├─ 1:N → Transaction ── N:1 → Category, Currency
 └─ 1:N → Budget ── N:1 → Category, Currency
```

### Key Design Decisions

| Decision | Why |
|---|---|
| **`base.html` vs `base_app.html`** | Public pages use top-nav; logged-in pages use left sidebar. Avoids CSS specificity wars. |
| **`Currency` + `UserCurrency`** | Currency is a global catalog. UserCurrency is a per-user join with `is_primary`. |
| **Signals for seeding** | `post_save` on `User` seeds 15 default categories + NGN as primary currency. |
| **Per-currency aggregation** | Never blend currencies — sum per currency, render per currency. |
| **Weighted moving average predictions** | 3-month and 6-month blended forecast for next month's income/expense. |
| **Print stylesheet for PDF** | Native browser print → PDF. Zero dependencies. |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Git**

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/asgatcreation/financeflow.git
cd financeflow

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser. 🎉

---

## 🔐 Environment Variables

Create a `.env` file at the project root:

```env
SECRET_KEY=your-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Optional — leave blank for SQLite
DATABASE_URL=
```

For production, `DATABASE_URL` should be your Supabase Session Pooler connection string:

```env
DATABASE_URL=postgresql://postgres.project:password@aws-0-region.pooler.supabase.com:5432/postgres?sslmode=require
```

> ⚠️ **Session pooler** works with Render's IPv4-only free tier. **Direct connection** does not.

---

## 🔑 Google OAuth Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. **APIs & Services** → **OAuth consent screen** → **External**
4. Fill in app name, support email, developer contact
5. Add test users
6. **Credentials** → **Create Credentials** → **OAuth client ID** → **Web application**

### 2. Authorized Redirect URIs

```
http://127.0.0.1:8000/accounts/google/login/callback/
https://your-app.onrender.com/accounts/google/login/callback/
```

### 3. Django Admin Setup

1. Copy **Client ID** and **Client Secret**
2. Log into `/admin/`
3. **Social Applications** → **Add social application**
4. Provider: `Google`, Name: `Google`
5. Paste the credentials
6. Move `example.com` to **Chosen sites**
7. Save

---

## ☁️ Deployment

### Render Blueprint

```yaml
services:
  - type: web
    name: financeflow-app
    plan: free
    runtime: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn expense_tracker.wsgi:application"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: PYTHON_VERSION
        value: "3.12.0"
      - key: WEB_CONCURRENCY
        value: "2"
      - key: DJANGO_SUPERUSER_USERNAME
        sync: false
      - key: DJANGO_SUPERUSER_EMAIL
        sync: false
      - key: DJANGO_SUPERUSER_PASSWORD
        sync: false
```

### Steps

1. Push repo to GitHub
2. [render.com](https://render.com) → **New** → **Blueprint**
3. Connect repo → **Apply**
4. Add env vars: `DATABASE_URL`, `DJANGO_SUPERUSER_*`
5. Deploy

---

## 🗺️ Roadmap

### ✅ Shipped

- [x] Multi-currency support (up to 5 per user)
- [x] Per-currency totals (no blended sums)
- [x] Google OAuth
- [x] Custom admin console with sidebar
- [x] CSV export with currency data
- [x] Modal logout confirmation
- [x] Split-screen auth pages
- [x] Page-load animation
- [x] 4 interactive charts + currency selector
- [x] Predictive insights on reports
- [x] PDF export from reports
- [x] PWA support (offline-first)
- [x] Excel (.xlsx) export
- [x] REST API with Django REST Framework

### 🚧 In Progress

- [ ] Recurring transactions
- [ ] Email reminders for budgets
- [ ] Receipt image uploads
- [ ] Shared wallets (multi-user budgets)

### 🔮 Planned

- [ ] Mobile app (React Native)
- [ ] Bank import (CSV, OFX)
- [ ] Currency conversion (live rates)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

**Asgat Creation**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/asgatcreation)
[![Live App](https://img.shields.io/badge/Live_App-10b981?style=for-the-badge&logo=render&logoColor=white)](https://financeflow-app-uuu8.onrender.com)

---

<div align="center">

**⭐ If this project helped you, please give it a star!**

Built with ❤️ using Django.

</div>