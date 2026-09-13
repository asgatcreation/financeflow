# 💰 FinanceFlow

A modern, production-ready **multi-currency expense tracker and finance dashboard** built with Django 5.

[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google](https://img.shields.io/badge/Google%20OAuth-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/identity)

[**🚀 Live Demo**](https://financeflow-app.onrender.com) · [**🐛 Report Bug**](../../issues)

> ⚠️ Hosted on Render's free tier — the first load may take ~30 seconds while the app wakes up.

---

## ✨ Features

| | Feature |
|---|---|
| 💱 | **Multi-currency** — Run up to 5 currencies simultaneously (NGN, USD, EUR, GBP, …) |
| 🔐 | **Authentication** — Custom signup/login + **Google OAuth** via django-allauth |
| 📊 | **Live dashboard** — Per-currency KPI cards, income/expense charts |
| 📈 | **Interactive reports** — 12-month trends + category donuts (Chart.js) |
| 🎯 | **Budgets** — Per-category limits with visual warnings at 80% / 100% |
| 🏷️ | **15+ pre-seeded categories** + custom category creation |
| 🚨 | **Overdue detection** — Auto-highlights expenses past deadline |
| 🔍 | **Search & filter** — By keyword, category, type, date range |
| 📥 | **CSV export** — One-click download of full history |
| 🛡️ | **Custom admin** — Sidebar navigation, model cards, dark login |
| 🌙 | **Modern UI** — Light fintech theme (Plus Jakarta Sans, emerald palette) |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 5.0 |
| **Language** | Python 3.12 |
| **Auth** | django-allauth + Google OAuth |
| **Database (prod)** | PostgreSQL (Render) |
| **Database (dev)** | SQLite |
| **Server** | Gunicorn |
| **Static Files** | Whitenoise |
| **Charts** | Chart.js 4 |
| **Hosting** | Render (Blueprint via `render.yaml`) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/financeflow-app.git
cd financeflow-app

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