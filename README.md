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
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge)](../../pulls)

<br/>

[**🚀 Live Demo**](https://financeflow-app-uuu8.onrender.com) · [**🐛 Report Bug**](../../issues) · [**✨ Request Feature**](../../issues)

> ⚠️ Hosted on Render's free tier — the first load may take ~30 seconds while the app wakes up.

<br/>

<img src="docs/screenshots/00-hero.gif" alt="FinanceFlow demo" width="100%" />

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

It's a showcase of **full-stack Django**: authentication, per-user data isolation, complex queries, aggregation, Chart.js integration, custom admin, and cloud deployment.

### 🎬 What It Does

📝 Sign up → 💱 Pick your currencies → 💸 Log transactions
↓
📊 Watch charts update → 🎯 Stay under budget → 📥 Export anytime


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

### 💸 Transactions — Mixed Currencies, Live Totals
![Transactions](docs/screenshots/05-transactions.png)

### 🎯 Budgets — Per-Category, Per-Currency Limits
![Budgets](docs/screenshots/06-budgets.png)

### 📈 Reports — 12-Month Trends + Category Breakdowns
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
- Per-currency **KPI cards** on the dashboard
- **20 currencies seeded** out of the box: 🇳🇬 NGN · 🇺🇸 USD · 🇪🇺 EUR · 🇬🇧 GBP · 🇯🇵 JPY · 🇨🇦 CAD · 🇦🇺 AUD · 🇮🇳 INR · 🇨🇳 CNY · 🇿🇦 ZAR · 🇬🇭 GHS · 🇰🇪 KES · 🇦🇪 AED · 🇸🇦 SAR · 🇨🇭 CHF · 🇧🇷 BRL · 🇲🇽 MXN · 🇸🇬 SGD · 🇭🇰 HKD · 🇰🇷 KRW
- Mark any currency as **primary** with a one-click star
- Remove currencies safely — blocked if transactions exist

### 🔐 Authentication
- **Email/password** registration with server-side validation
- **Google OAuth** via `django-allauth`
- Split-screen login/signup with **rotating slides** (auto-plays + manual dots)
- **Modal-based logout** confirmation — never a jarring redirect
- Password reset flow (forgot password)
- **Per-user data isolation** — you only see your own data, ever

### 📊 Dashboard
- **Per-currency summary cards** — balance, monthly income, monthly expense
- **4 interactive Chart.js charts** — 6-month trend, expense donut, income donut, savings bar
- **Currency selector** — switch all charts between your currencies
- Recent transactions feed
- Monthly budget progress with visual warnings
- Friendly empty states for new users

### 💸 Transactions
- Full CRUD with inline validation
- **Currency picker next to date** — sensible "when + how much" grouping
- Categories filter automatically by transaction type
- **Advanced filters** — search, type, category, date range
- **Live filtered totals** — income/expense/net recalculate on every filter change
- Pagination (15 per page)
- **CSV export** — download full history anytime

### 🎯 Budgets
- Set monthly limits per category + per currency
- **Progress bars** with color states:
  - 🟢 Emerald (safe, < 80%)
  - 🟡 Amber (warning, 80–100%)
  - 🔴 Red (over budget)
- Dashboard shows current-month budgets inline
- Dedicated budgets grid with big figures

### 📈 Reports
- **12-month bar chart** — income vs expense, side by side
- **Category donuts** — expense and income breakdowns for the current month
- **Currency selector** — filter all reports by a single currency
- Fully interactive (hover for values)

### 🏷️ Categories
- **15 pre-seeded categories** on signup: 💰 Salary · 💻 Freelance · 📈 Investments · 🎁 Gifts · 🛒 Groceries · 🏠 Rent · 🚗 Transport · 🍽️ Dining · 💡 Utilities · 💊 Healthcare · 🎬 Entertainment · 🛍️ Shopping · 📚 Education · 💻 Subscriptions · 🏋️ Fitness
- **21 icon choices** with labels
- **11 color options** for visual distinction in charts
- Fully editable / deletable per user

### 🛡️ Custom Admin Console
- **Sidebar navigation** (260px, collapsible on mobile)
- **Quick Action tiles** at the top — Add user, Transactions, Social apps, Currencies
- **Model cards** with icons, descriptions, and dual actions (View all / Add)
- **Custom split-screen admin login** — dark green gradient brand panel
- **Recent activity feed**
- **Mobile hamburger menu** with slide-in sidebar

### 🎨 Design System
- **Plus Jakarta Sans** typography (400/500/600/700/800)
- **Emerald primary** (#10b981) + rose accents
- **Light, airy surfaces** with subtle shadows and 16–24px radii
- **Zero build step** — plain CSS, no Tailwind, no Webpack
- **Responsive** — mobile-first, sidebar collapses at 900px
- **Page-load animation** — smooth fade-in on every page
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
- Vanilla JS (carousel, modals, mobile menu, page loader)
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

financeflow/
├── accounts/ # User app (legacy auth views)
├── finance/ # Core finance app
│ ├── models.py # Category, Transaction, Budget, Currency, UserCurrency
│ ├── forms.py # All ModelForms + validation
│ ├── views.py # Dashboard, CRUD, Reports, Currencies
│ ├── urls.py # app_name = "finance"
│ ├── admin.py # Custom admin configs
│ ├── utils.py # Helpers (month_range, series)
│ └── migrations/
├── expense_tracker/ # Project config
│ ├── settings.py # Env-driven, prod-ready
│ ├── urls.py
│ └── wsgi.py
├── templates/
│ ├── account/ # allauth templates
│ │ ├── login.html
│ │ └── signup.html
│ ├── admin/ # Custom admin overrides
│ │ ├── base_site.html # Sidebar + theme
│ │ ├── login.html # Split-screen
│ │ ├── index.html # Dashboard
│ │ └── app_list.html
│ ├── finance/
│ │ ├── landing.html
│ │ ├── dashboard.html
│ │ ├── transactions.html
│ │ ├── transaction_form.html
│ │ ├── budgets.html
│ │ ├── reports.html
│ │ ├── currencies.html
│ │ └── categories.html
│ ├── base.html # Public layout
│ └── base_app.html # Logged-in layout (sidebar)
├── static/
│ └── css/style.css # Full design system
├── docs/screenshots/ # README images
├── build.sh # Render build script
├── render.yaml # Render blueprint
├── requirements.txt
├── .env.example
├── .gitignore
└── manage.py

### Data Model
User (Django)
├─ 1:N → UserCurrency ── N:1 → Currency (global catalog)
├─ 1:N → Category (per-user, with icon + color + type)
├─ 1:N → Transaction ── N:1 → Category
│ └─ N:1 → Currency
└─ 1:N → Budget ── N:1 → Category
└─ N:1 → Currency


### Key Design Decisions

| Decision | Why |
|---|---|
| **`base.html` vs `base_app.html`** | Public pages use top-nav; logged-in pages use left sidebar. Separation avoids CSS specificity wars. |
| **`Currency` + `UserCurrency`** | Currency is a global catalog (20 rows). UserCurrency is a per-user join with `is_primary`. Lets each user track NGN + USD + EUR without global state. |
| **Signals for seeding** | `post_save` on `User` seeds 15 default categories + NGN as primary. Zero-config onboarding. |
| **Per-user filtering** | Every view filters `filter(user=self.request.user)`. No leaks possible. |
| **Admin theme via CSS specificity** | Django admin's `#content h1` has specificity 101. Custom rules scoped under `#content .admix-hero h1` win cleanly. |
| **Whitenoise + Gunicorn** | No CDN needed; static files served from the same origin. Fast enough for portfolio use. |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Git**
- *(Optional)* A [Google Cloud Console](https://console.cloud.google.com/) project for OAuth
- *(Optional)* A [Supabase](https://supabase.com/) project for production DB

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/asgatcreation/financeflow.git
cd financeflow

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env         # Windows
cp .env.example .env           # macOS / Linux

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver




