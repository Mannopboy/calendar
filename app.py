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

    def add(self):
        db.session.add(self)
        db.session.commit()


class Month(db.Model):
    __tablename__ = "month"
    id = Column(Integer, primary_key=True)
    month = Column(Integer)
    years_id = Column(Integer, ForeignKey('years.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()


class Days(db.Model):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True)
    day = Column(Integer)
    month = Column(Integer, ForeignKey('month.id'))
    year = Column(Integer, ForeignKey('years.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()


class DayLessons(db.Model):
    __tablename__ = "day_lessons"
    id = Column(Integer, primary_key=True)
    days = Column(Integer, ForeignKey('days.id'))
    status = Column(Boolean)


list_days = []


def get_calendar(current_year, next_year):
    for year in range(current_year, next_year + 1):
        if next_year:
            range_number = 6
        else:
            range_number = 13
        for month in range(1, range_number):
            object_days = {
                'month': month,
                'days': [],
                'year': year
            }
            if month == 7 or month == 6 or month == 8:
                pass
            else:
                month_name = calendar.month_name[month]
                cal = calendar.monthcalendar(year, month)
                for week in cal:
                    for day in week:
                        day_str = str(day) if day != 0 else "  "
                        if day != 0:
                            object_days['days'].append(day_str)
                            day_of_week = calendar.day_name[calendar.weekday(year, month, day)]
            list_days.append(object_days)

    for year in list_days:
        year_b = Years.query.filter(Years.year == year["year"]).first()
        if not year_b:
            year_new = Years(year=year['year'])
            year_new.add()


@app.route('/')
def hello_world():
    print(get_calendar(2023, 2024))
    return render_template('index.html')


if __name__ == 'main':
    app.run()
