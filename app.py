from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from flask_migrate import Migrate
import calendar
from datetime import datetime
from pprint import pprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config['SECRET_KEY'] = '123'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Years(db.Model):
    __tablename__ = 'years'
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = db.relationship('Month', backref='years', order_by='Month.id')

    def add(self):
        db.session.add(self)
        db.session.commit()


class Month(db.Model):
    __tablename__ = "month"
    id = Column(Integer, primary_key=True)
    month_number = Column(Integer)
    month_name = Column(String)
    years_id = Column(Integer, ForeignKey('years.id'))
    days = db.relationship('Days', backref='month', order_by='Days.id')

    def add(self):
        db.session.add(self)
        db.session.commit()


class Days(db.Model):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True)
    day_number = Column(Integer)
    day_name = Column(String)
    month_id = Column(Integer, ForeignKey('month.id'))
    year_id = Column(Integer, ForeignKey('years.id'))

    # daily_lesson = db.relationship('DailyLesson', backref='days', order_by='DailyLesson.id')

    def add(self):
        db.session.add(self)
        db.session.commit()


class DailyLesson(db.Model):
    __tablename__ = "daily_lesson"
    id = Column(Integer, primary_key=True)
    days = Column(Integer, ForeignKey('days.id'))
    status = Column(Boolean)


list_days = []


def get_calendar(current_year, next_year):
    for year in range(current_year, next_year + 1):
        for month in range(1, 13):
            if (year == current_year and month not in [1, 2, 3, 4, 5, 6, 7, 8]) or (
                    year == next_year and month not in [6, 7, 8, 9, 10, 11, 12]):
                month_name = calendar.month_name[month]
                object_days = {
                    'month_number': month,
                    'month_name': month_name,
                    'days': [],
                    'year': year
                }
                cal = calendar.monthcalendar(year, month)
                for week in cal:
                    for day in week:
                        day_str = str(day) if day != 0 else "  "
                        if day != 0:
                            if 1 <= day <= calendar.monthrange(year, month)[1]:
                                weeks_id = calendar.weekday(year, month, day)
                                day_name = calendar.day_name[weeks_id]
                            day_object = {
                                'day_number': day_str,
                                'day_name': day_name
                            }
                            object_days['days'].append(day_object)
                list_days.append(object_days)
    for year in list_days:
        year_b = Years.query.filter(Years.year == year["year"]).first()
        if not year_b:
            year_new = Years(year=year['year'])
            year_new.add()
        year_b = Years.query.filter(Years.year == year["year"]).first()
        if year_b:
            month_b = Month.query.filter(Month.month_number == year['month_number'],
                                         Month.years_id == year_b.id).first()
            if not month_b:
                month = Month(month_number=year['month_number'], month_name=year['month_name'], years_id=year_b.id)
                month.add()
                month_one = Month.query.filter(Month.month_number == year['month_number']).first()
                for day in year['days']:
                    day_b = Days.query.filter(Days.day_number == day['day_number'], Days.month_id == month_one.id,
                                              Days.year_id == year_b.id).first()
                    if not day_b:
                        new_day = Days(day_number=day['day_number'], day_name=day['day_name'],
                                       month_id=month_one.id, year_id=year_b.id)
                        new_day.add()


@app.route('/')
def hello_world():
    get_calendar(datetime.now().year, datetime.now().year + 1)
    return render_template('index.html')


if __name__ == 'main':
    app.run()
