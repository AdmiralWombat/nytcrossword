from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Score
from django.db.models import F, OuterRef, Subquery

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

            d += f'<li> <div><div class=day_left>{score.name} :</div><div class=day_right> {score.time}</div></div></li>'
            count = count + 1

        if len(scores_per_day) > max_count:
            d += f'<li> more... </li>'
        if day != 0:
            return f"<td><div class=date_box><span class='date'>{day}</span><ul> {d} </ul></div></td>"
        return '<td><div class=date_box></div></td>'

    def formatweek(self, theweek, scores):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, scores)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        scores = Score.objects.filter(date__year=self.year, date__month=self.month)

        cal = f'<table border="1" cellpadding="5" cellspacing="5" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, scores)}\n'
        return cal