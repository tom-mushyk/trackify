from flask import Flask, session, request, render_template, url_for, flash, redirect
from forms import LoginForm, RegisterForm, AddTaskForm, AddLinkForm, AddWeatherForm
from models import db, User, Task, Link, CityCard
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_migrate import Migrate
from datetime import datetime
from helper import getFaviconUri
import urllib3
import json



app = Flask(__name__)
app.config['SECRET_KEY'] = 'keysample'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('.user', username=current_user.username))

    else:
        form = LoginForm()
        if form.validate_on_submit():
            checkedUser = User.query.filter_by(username=form.username.data, password_hash=form.password.data).first()
            if checkedUser is not None:
                login_user(checkedUser)
                return redirect(url_for('.user', username=current_user.username))
            else:
                flash(u'Wrong password!'.format(form.username.data), 'error')
                return redirect(url_for('.login'))

        return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'You are logged out', 'success')
    return redirect(url_for('.login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated == True:
        return redirect(url_for('.user', username=current_user.username))
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.password_hash = form.password.data
            user.email = form.email.data

            user_check = User.query.filter_by(username=form.username.data, email=form.email.data).first()
            if user_check is None:
                    db.session.add(user)
                    db.session.commit()
                    flash(u'Now you can Sign In', 'success')
                    return redirect(url_for('.login'))
            else:
                flash(u'Username or Email is used by another User, choose other name', 'error')

        return render_template('auth/register.html', form=form)

@app.route('/')
@app.route('/about')
def about():
    if current_user.is_authenticated == True:
        return redirect(url_for('.user', username=current_user.username))
    else:
        return render_template('about.html')


@app.route('/user/<string:username>')
@login_required
def user(username):
        tasksCount = Task.query.filter_by(user_id = current_user.id).count()
        linksCount = Link.query.filter_by(user_id = current_user.id).count()
        cityCardsCount = CityCard.query.filter_by(user_id=current_user.id).count()
        return render_template('user.html', user = username, tasksCount = tasksCount, linksCount = linksCount, cityCardsCount = cityCardsCount)

@app.route('/dashboard/<app_name>', methods=['GET', 'POST'])
@login_required
def dashboard(app_name):

    if app_name == 'tasks':
        form = AddTaskForm()
        tasks = Task.query.filter_by(user_id = current_user.id)
        print(current_user.id)
        if form.validate_on_submit():
            task = Task()
            task.title = form.title.data
            task.description = form.description.data
            task.dateAdded = datetime.utcnow()
            task.user_id = current_user.id

            print(task)

            try:
                db.session.add(task)
                db.session.commit()
                flash(u'Task {} Added!'.format(task.title), 'success')
                return redirect(url_for('.dashboard', app_name="tasks"))

            except:
                flash(u'Cant add this task', 'error')
                return redirect(url_for('.dashboard', app_name="tasks"))
        return render_template('dashboard_apps/tasks.html', form=form, tasks=tasks)

    elif app_name == 'links':
        form = AddLinkForm()
        links = Link.query.filter_by(user_id = current_user.id)
        if form.validate_on_submit():
            link = Link()
            link.title = form.title.data
            link.url = form.url.data
            link.domain = getFaviconUri(link.url)
            link.user_id = current_user.id

            try:
                db.session.add(link)
                db.session.commit()
                flash(u'Site {} Added!'.format(link.title), 'success')
                return redirect(url_for('.dashboard', app_name="links"))

            except:
                flash(u'Cant add link to {}'.format(link.title), 'error')
                return redirect(url_for('.dashboard', app_name="links"))
        return render_template('dashboard_apps/links.html', form=form, links=links)

    elif app_name == 'weather':
        cards = CityCard.query.filter_by(user_id = current_user.id)
        form = AddWeatherForm()
        appid = 'a7decb12f5f033829a2d5d0adc40c03a'
        if form.validate_on_submit():
            cityCard = CityCard()
            cityName = form.name.data
            http = urllib3.PoolManager()
            r = http.request('GET',
                                 'api.openweathermap.org/data/2.5/weather?q={}'.format(cityName) + '&APPID={}'.format(
                                     appid))


            if r.status != 404:
                x = json.loads(r.data)
                weather = x['weather']
                main = x['main']

                cityCard.name = form.name.data
                for item in weather:
                    print(item)
                print (item['main'])

                cityCard.main = item['main']
                cityCard.description = item['description']

                mainTemp = round(((main['temp'])-273.15), 1)
                cityCard.temp = mainTemp
                cityCard.pressure = main['pressure']
                cityCard.user_id = current_user.id


                try:
                    db.session.add(cityCard)
                    db.session.commit()
                    flash(u'City {} added!'.format(cityCard.name), 'success')
                    return redirect(url_for('.dashboard', app_name="weather"))

                except:
                    flash(u'Can\'t add city {}'.format(cityCard.name), 'error')
                    return redirect(url_for('.dashboard', app_name="weather"))

            else:
                flash(u'City {} doesn\'t exist'.format(cityCard.name), 'error')
                return redirect(url_for('.dashboard', app_name="weather"))

        return render_template('dashboard_apps/weather.html', form=form, cards=cards)

@app.route('/deleteTask/<int:id>/', methods=['GET', 'POST'])
@login_required
def deleteTask(id):
    try:
        print(id)
        Task.query.filter_by(id=id).delete()
        db.session.commit()
        flash(u'Task deleted!', 'success')
        return redirect(url_for('.dashboard', app_name="tasks"))
    except:
        flash(u'Can\'t delete task!', 'error')
        return redirect(url_for('.dashboard', app_name="tasks"))

@app.route('/deleteCityCard/<int:id>/', methods=['GET', 'POST'])
@login_required
def deleteCityCard(id):
    try:
        print(id)
        CityCard.query.filter_by(id=id).delete()
        db.session.commit()
        flash(u'City deleted!', 'success')
        return redirect(url_for('.dashboard', app_name="weather"))
    except:
        flash(u'Can\'t delete this city!', 'error')
        return redirect(url_for('.dashboard', app_name="weather"))

@app.route('/deleteLink/<int:id>/<string:title>', methods=['GET', 'POST'])
@login_required
def deleteLink(id, title):
    try:
        print(id)
        Link.query.filter_by(id=id).delete()
        db.session.commit()
        flash(u'Site deleted!', 'success')
        return redirect(url_for('.dashboard', app_name="links"))
    except:
        flash(u'Can\'t delete {}!'.format(title), 'error')
        return redirect(url_for('.dashboard', app_name="links"))

@app.route('/redirectTo/<int:id>/<string:title>', methods=['GET', 'POST'])
@login_required
def redirectTo(id, title):
    try:
        print(id)
        link = Link.query.filter_by(id=id).first()
        return redirect(link.url, code=302)
    except:
        flash(u'Can\'t redirect to {}!'.format(title), 'error')
        return redirect(url_for('.dashboard', app_name="links"))


if __name__== '__main__':
    app.run(debug=True)

    