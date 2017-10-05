# =============================================================================
# Journal.py: Simple Personal Journalling app
# Uses Flask, WTForms 
# =============================================================================
# Copyright Stuart McIntosh 2017
# s.g.mcintosh@gmail.com
# ============================================================================= 

from flask import Flask, g, render_template, redirect, flash, url_for, abort
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)


import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'skjdfds.kfjhdsfkjdhsfkdshfkdshjfdskjfhs'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    ''' flask class that manages user logins. Pass in the current userid from
        the User model (table). make sure that the models exists if not return
        None
    '''
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    ''' Connect to the database before each request '''
    # g is a flask global variable, it is availble always
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    ''' Close the database and return the response after each request'''
    g.db.close()
    return response

@app.route('/login', methods=('GET', 'POST'))
@app.route('/', methods=('GET', 'POST'))
def index():
    ''' Login / index view - checks the database to ensure that the user exists
        the sends the user back to the index page
        1. Validate all entries match our validators - validate_on_submit
        2. Check, the email exists
        3. Check the password that was encrypted via Flask Bcrypt
        4. If all good - login the user via flask login_manager / login_user
    '''
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesnt match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "Success")
                return redirect(url_for('journals'))
            else:
                flash("Your email or password doesnt match!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    ''' Login out - we can run this if the user is actually logged in
        we check this vis the decorator @login_required
    '''
    # remove the session cookie created in the login_user
    logout_user()
    flash("Youv'e been logged out, come back soon!", "success")
    return redirect(url_for('index'))

@app.route('/new', methods=('GET', 'POST'))
def new_journal():
    ''' post a new journal '''
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Journal.create(user=g.user._get_current_object(),
                              title=form.title.data.strip(),
                              entry_date=form.entry_date.data,
                              duration=form.duration.data,
                              learnings=form.learnings.data.strip(),
                              resources=form.resources.data,
                              tags=form.tags.data)
        flash("Journal posted", "success")
        return redirect(url_for('journals'))
    return render_template('new.html', form=form)

@app.route('/journals', methods=('GET', 'POST'))
def journals():
    ''' view to show all the current posted journals '''
    stream = current_user.get_entries()
    user = current_user
    return render_template('journals.html', stream=stream, user=user)

@app.route('/tags/<tag>', methods=('GET', 'POST'))
def tags(tag):
    ''' view to show all the current posted journals by a tag'''
    stream = current_user.get_all_tagged_entries(tag)
    user = current_user
    return render_template('journals.html', stream=stream, user=user, tag=tag)

@app.route('/details/<title>', methods=('GET', 'POST'))
def details(title):
    ''' view to the details of a single entry '''
    stream = current_user.get_entries().where(models.Journal.title == title)
    return render_template('details.html', stream=stream)

@app.route('/delete/<title>')
@login_required
def delete(title):
    ''' removes the journal entry based on the title '''
    try:
        # delete the following journal
        remove_title = models.Journal.delete().where(models.Journal.title == title)
        remove_title.execute()
    except models.IntegrityError:
        abort(404)
    else:
        flash("You've deleted {}!".format(title), 'success')
    return redirect(url_for('journals'))

@app.route('/edit/<title>', methods=('GET', 'POST'))
def edit(title):
    ''' edit a journal '''
    try:
        entry = models.Journal.select().where(models.Journal.title==title).get()
    except models.DoesNotExist:
        abort(404)
    else:
        form = forms.EntryForm(obj=entry)
        if form.validate_on_submit():
            entry.user=g.user._get_current_object()
            entry.title=form.title.data.strip()
            entry.entry_date=form.entry_date.data
            entry.duration=form.duration.data
            entry.learnings=form.learnings.data
            entry.resources=form.resources.data
            entry.tags=form.tags.data
            entry.save()
            flash("You've updated :  {}!".format(title), 'success')
            return redirect(url_for('journals'))
    return render_template('edit.html', entry=entry, form=form)

@app.errorhandler(404)
def not_found(error):
    ''' manage any erros that may come from using the app '''
    return render_template('404.html'), 404

@app.route('/help')
def help():
    ''' show a help page '''
    return render_template('help.html')

@app.route('/modal')
def modal():
    ''' show a help page '''
    return render_template('modal.html')

@app.template_filter()
def split_string(string):
    ''' split string in template by delimiter '''
    return string.strip().split(',')  

@app.template_filter()
def remove_wspace(string):
    ''' remove all whitespace '''
    return string.strip()

if __name__ == '__main__':
    ''' run the app '''
    models.initalize()
    try:
        models.User.create_user(email='s.g.mcintosh@gmail.com',
                                password='password'
                               )
    except ValueError:
        pass

    # run the app in debug mode
    app.run(debug=DEBUG, host=HOST, port=PORT,)
