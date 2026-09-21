from django.shortcuts import render


def csrf_failure(request, reason=""):
    """Show the 403 page on CSRF errors instead of Django's default."""
    return render(request, "403.html", status=403)