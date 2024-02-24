from django.urls import path, include

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<int:player_id>/", views.stats, name="stats"),
    path("calendar", views.CalendarView.as_view(), name="calendar"),
    path("graph", views.graph, name="stats"),
]