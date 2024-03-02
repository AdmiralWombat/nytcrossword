from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.http import Http404
import datetime as dt
from datetime import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import pandas as pd
from django.db.models import F, Avg
from django.views import generic
from django.utils.safestring import mark_safe

from .models import Player
from .models import Score
from django.db.models.aggregates import Min, Max, Count

from .utils import Calendar

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d_obj):
    first = d_obj.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d_obj):
    days_in_month = calendar.monthrange(d_obj.year, d_obj.month)[1]
    last = d_obj.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

class CalendarView(generic.ListView):
    model = Score
    template_name = 'leaderboard/calendar.html'
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)

        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        return context

def get_top_5_time_averages():
    """
    Gets the top 5 players with the highest average time scores.
    """

    top_players = (
        Score.objects.values('name__id', 'name__name')
        .annotate(time_seconds=Avg(F('time__hour') * 3600 + F('time__minute') * 60 + F('time__second')))
        .order_by('time_seconds')[:5]
    )

    return top_players

def get_top_5_time_bests():
    top_players = (
        Player.objects.annotate(
            best_time=Min('score__time'),
            score_count=Count('score')
        )
        .filter(score_count__gt=0)
        .order_by('best_time')[:5]
    )
    result = []
    for player in top_players:
        result.append({
            'name__name': player.name,
            'name__id': player.pk,
            'best_time': player.best_time
        })
    return result

def get_top_5_time_worsts():
    top_players = (
        Player.objects.annotate(
            best_time=Max('score__time'),
            score_count=Count('score')
        )
        .filter(score_count__gt=0)
        .order_by('-best_time')[:5]
    )
    result = []
    for player in top_players:
        result.append({
            'name__name': player.name,
            'name__id': player.pk,
            'best_time': player.best_time
        })
    return result
def get_scores_by_weekday(player_id, day_of_week):
    best = "invalid"
    worst = "invalid"
    avg = "invalid"
    best_percent = ""
    worst_percent = ""
    avg_percent = ""

    day_of_week_scores = Score.objects.filter(name__pk=player_id, date__week_day=day_of_week).order_by('time')

    if day_of_week_scores:
        best = day_of_week_scores.first().time.strftime("%M:%S")
        worst = day_of_week_scores.last().time.strftime("%M:%S")

        total_seconds = sum(
            score.time.hour * 3600 + score.time.minute * 60 + score.time.second for score in day_of_week_scores)
        avg_seconds = total_seconds // len(day_of_week_scores)
        avg_hours, avg_seconds = divmod(avg_seconds, 3600)
        avg_minutes, avg_seconds = divmod(avg_seconds, 60)
        average_time = dt.time(avg_hours, avg_minutes, avg_seconds)
        avg = average_time.strftime("%M:%S")

    return [best, worst, avg, best_percent, worst_percent, avg_percent]
def stats(request, player_id):
    player = get_object_or_404(Player, pk=player_id)

    sunday_scores = get_scores_by_weekday(player_id, 1)
    monday_scores = get_scores_by_weekday(player_id, 2)
    tuesday_scores = get_scores_by_weekday(player_id, 3)
    wednesday_scores = get_scores_by_weekday(player_id, 4)
    thursday_scores = get_scores_by_weekday(player_id, 5)
    friday_scores = get_scores_by_weekday(player_id, 6)
    saturday_scores = get_scores_by_weekday(player_id, 7)

    context = {
        "player": player,
        "best_time": [monday_scores[0], tuesday_scores[0], wednesday_scores[0], thursday_scores[0], friday_scores[0], saturday_scores[0], sunday_scores[0]],
        "worst_time": [monday_scores[1], tuesday_scores[1], wednesday_scores[1], thursday_scores[1], friday_scores[1], saturday_scores[1], sunday_scores[1]],
        "average_time": [monday_scores[2], tuesday_scores[2], wednesday_scores[2], thursday_scores[2], friday_scores[2], saturday_scores[2], sunday_scores[2]],
        "best_percent": [monday_scores[3], tuesday_scores[3], wednesday_scores[3], thursday_scores[3], friday_scores[3], saturday_scores[3], sunday_scores[3]],
        "worst_percent": [monday_scores[4], tuesday_scores[4], wednesday_scores[4], thursday_scores[4], friday_scores[4], saturday_scores[4], sunday_scores[4]],
        "average_percent": [monday_scores[5], tuesday_scores[5], wednesday_scores[5], thursday_scores[5], friday_scores[5], saturday_scores[5], sunday_scores[5]],
    }
    return render(request, "leaderboard/stats.html", context)



def graph(request):
    return render(request, "leaderboard/calendar.html", { })

def index(request):
    try:
        id = int(request.GET.get('id'))
        type = request.GET.get('type', 'default')
    except:
        id = 0

    player_list = Player.objects.order_by("-name")

    type = "Average Time"
    if id == 0:
        type = "Average Time"
        time_results = get_top_5_time_averages()

        for player in time_results:
            time_seconds = player['time_seconds']
            player['best_time'] = time(int(time_seconds // 3600),
                                       (int(time_seconds % 3600) // 60),
                                       int(time_seconds % 60))
    elif id == 1:
        type = "Best Time"
        time_results = get_top_5_time_bests()
    elif id == 2:
        type = "Worst Time"
        time_results = get_top_5_time_worsts()



    context = {
        "player_list": player_list,
        "time_1_name": time_results[0]['name__name'] if len(time_results) > 0 else "-",
        "time_2_name": time_results[1]['name__name'] if len(time_results) > 1 else "-",
        "time_3_name": time_results[2]['name__name'] if len(time_results) > 2 else "-",
        "time_4_name": time_results[3]['name__name'] if len(time_results) > 3 else "-",
        "time_5_name": time_results[4]['name__name'] if len(time_results) > 4 else "-",
        "time_1_id": time_results[0]['name__id'] if len(time_results) > 0 else "",
        "time_2_id": time_results[1]['name__id'] if len(time_results) > 1 else "",
        "time_3_id": time_results[2]['name__id'] if len(time_results) > 2 else "",
        "time_4_id": time_results[3]['name__id'] if len(time_results) > 3 else "",
        "time_5_id": time_results[4]['name__id'] if len(time_results) > 4 else "",
        "time_1_score": time_results[0]['best_time'].strftime("%M:%S") if len(time_results) > 0 else "-",
        "time_2_score": time_results[1]['best_time'].strftime("%M:%S") if len(time_results) > 1 else "-",
        "time_3_score": time_results[2]['best_time'].strftime("%M:%S") if len(time_results) > 2 else "-",
        "time_4_score": time_results[3]['best_time'].strftime("%M:%S") if len(time_results) > 3 else "-",
        "time_5_score": time_results[4]['best_time'].strftime("%M:%S") if len(time_results) > 4 else "-",
        "type": type
    }
    return render(request, "leaderboard/index.html", context)