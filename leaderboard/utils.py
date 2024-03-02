from datetime import datetime, timedelta, date
from calendar import HTMLCalendar
from .models import Score
from django.db.models import F, OuterRef, Subquery

import calendar

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()


    def formatday(selfself, day, scores):
        max_count = 2
        scores_per_day = scores.filter(date__day=day).order_by('time')[:max_count+1]
        d = ''
        count = 0
        for score in scores_per_day:
            if count >= max_count:
                break

            formattedTime = score.time.strftime("%M:%S")
            d += f'<li>{score.name}:<span class=day_right>{formattedTime}</span></li>'
            count = count + 1

        if len(scores_per_day) > max_count:
            d += f'<li> more... </li>'
        if day != 0:
            return f"<td><div class=date_box><span class='date'>{day}</span><ul class=day_list_ul> {d} </ul></div></td>"
        return '<td><div class=date_box></div></td>'

    def formatweek(self, theweek, scores):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, scores)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        scores = Score.objects.filter(date__year=self.year, date__month=self.month)

        cal = f'<table border="1" cellpadding="5" cellspacing="5" class="calendar">\n'
        cal += f'<tr><th colspan="7" class="month">'
        prev_link = f'/leaderboard/calendar?{self.prev_month()}'
        cal += f'<a class="calendar_prev_month" href="{prev_link}"><i class="material-symbols-outlined">arrow_back</i></a>'
        cal += f'{calendar.month_name[self.month]} {self.year}'
        next_link = f'/leaderboard/calendar?{self.next_month()}'
        cal += f'<a class="calendar_next_month" href="{next_link}"><i class="material-symbols-outlined">arrow_forward</i></a>'
        cal += f'</th></tr>\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, scores)}\n'
        return cal

    def prev_month(self):
        first = date(self.year, self.month, 1)
        prev_month = first - timedelta(days=1)
        month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
        return month

    def next_month(self):
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        last = date(self.year, self.month, days_in_month)
        next_month = last + timedelta(days=1)
        month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
        return month
    