from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
from models import initialize_db, Schedule
import scheduler

app = Flask(__name__)
app.secret_key = os.urandom(24)
WTF_CSRF_SECRET_KEY = app.secret_key

TEMPLATES_AUTO_RELOAD = True

csrf = CSRFProtect(app)
csrf.init_app(app)

class DosageForm(FlaskForm):
    medicineName = StringField('Name of medicine', [validators.Length(min=4, max=25), DataRequired()])
    boxName = StringField('Enter IP or Name of box', [validators.Length(min=4, max=25), DataRequired()])
    afterWhat = SelectField('After What event', choices=[('bfm', 'Before Meals'), ('afm', 'After Meals'), ('rm', 'Random')])
    numberTabs = IntegerField('Tablets per Dose', [DataRequired()])
    submit = SubmitField("Create")

@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}

@app.route("/logs")
def logs():
   # Pass the template data into the template main.html and return it to the user
   return render_template('logs.html')

@app.errorhandler(CSRFError)
def csrf_error(reason):
    return render_template('csrf_error.html', reason=reason), 400

@app.route("/boxes")
def boxes():
    table_data = Schedule.select()
    return render_template('boxes.html', table_data = table_data)

@app.route("/esp/<boxName>")
def pingMe(boxName):
    table_data = Schedule.select()
    scheduler.send_mqtt("esp/" + boxName, "Ping Message")
    return render_template('boxes.html', table_data = table_data)

@app.route("/", methods=["GET" , "POST"])
def home():
    form = DosageForm()
    if form.validate_on_submit():
        new_med = Schedule.create(
            medicineName = form.medicineName.data,
            boxName = form.boxName.data,
            afterWhat = form.afterWhat.data,
            numberTabs = form.numberTabs.data
        )
        flash("Record successfully saved")
        return redirect(url_for('home'))
    return render_template('main.html', form=form)

def main():
    app.run(host='0.0.0.0', port=8181, debug=True)
    scheduler.check()

if __name__ == "__main__":
    initialize_db()
    main()