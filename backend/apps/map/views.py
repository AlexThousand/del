from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    Отображает главную страницу с картой.
    """
    context = {
        'page_title': 'Test map',
        'map_width': 8,
        'sidebar_width': 4,
        'show_sidebar': True,
        'map_type': 'main'
    }
    return render(request, "map_base.html", context)

@login_required
def point(request):
    """
    Отображает страницу с логикой построение оптимального маршрута
    между точками
    """
    context = {
        'page_title': 'Point map',
        'map_width': 12,
        'show_sidebar': False,
        'map_type': 'point'
    }
    return render(request, "map_base.html", context)

@login_required
def point_alt(request):
    """
    Отображает логику построение множества маршрутов между точками
    """
    context = {
        'page_title': 'Point map (Alternative)',
        'map_width': 12,
        'show_sidebar': False,
        'map_type': 'point_alt'
    }
    return render(request, "map_base.html", context)