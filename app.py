from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from flask_migrate import Migrate
import calendar
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
    month = Column(Integer)
    years_id = Column(Integer, ForeignKey('years.id'))
    days = db.relationship('Days', backref='month', order_by='Days.id')

    def add(self):
        db.session.add(self)
        db.session.commit()


class Days(db.Model):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True)
    day = Column(Integer)
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
                object_days = {
                    'month': month,
                    'days': [],
                    'year': year
                }
                month_name = calendar.month_name[month]
                cal = calendar.monthcalendar(year, month)
                for week in cal:
                    for day in week:
                        day_str = str(day) if day != 0 else "  "
                        if day != 0:
                            object_days['days'].append(day_str)
                list_days.append(object_days)
    print(list_days)
    for year in list_days:
        year_b = Years.query.filter(Years.year == year["year"]).first()
        if not year_b:
            year_new = Years(year=year['year'])
            year_new.add()
        if year_b:
            month = Month(month=year['month'], years_id=year_b.id)
            month.add()
            month_one = Month.query.filter(Month.month == year['month']).first()
            for day in year['days']:
                new_day = Days(day=day, month_id=month_one.id, year_id=year_b.id)
                new_day.add()


@app.route('/')
def hello_world():
    print(get_calendar(2023, 2024))
    return render_template('index.html')


if __name__ == 'main':
    app.run()
