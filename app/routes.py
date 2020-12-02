from app import app
from app import mail
from app.database import *
from flask import render_template, request, flash, redirect, url_for, session
from functools import wraps
from flask_mail import Message
import smtplib

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if is_valid_user_id(session['user_id']):
                return f(*args, **kwargs) # We found a valid user
        app.logger.warning("No session, this pages requires login")
        flash("This pages requires you to sign-in")
        return redirect(url_for('login'))    
    return decorated_function

@app.route('/')
def homepage():
    user = None
    if 'user_id' in session:
        user_id = session['user_id']
        try: 
            user = get_user(user_id)
        except Exception:
            app.logger.error("User ID from previous session")
    
    return render_template('home.html.j2', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            if check_password(email, password):
                flash("Authentication succeeded")
                user_id = get_user_id(email)
                session['user_id'] = user_id
                return redirect(url_for('homepage'))
            else:
                flash("Failed to authenticate")
        
    return render_template('login.html.j2')

@app.route('/logout')
def logout():
    session.clear()
    flash("signed out")
    return redirect(url_for('homepage'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            try:
                create_user(email, password)
                flash(f"User '{email}' created")
                return redirect(url_for('homepage'))
            except Exception as ex:
                app.logger.error('Could not register: {}'.format(ex), exc_info=True)
                flash("Failed to register")
       
    return render_template('register.html.j2')

@app.route('/admin')
@login_required
def admin():
    return "Only signed in users can see this"

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']

    if request.method == 'POST':
        if 'nickname' in request.form:
            # Inform user their Nickname is taken.
            new_nickname = request.form['nickname']
            user_nickname = new_nickname
            if nickname_exists(user_nickname):
                flash('That nickname is taken. Please choose another one!')
            else: 
                save_nickname(user_id, request.form['nickname'])
        elif 'verifyme' in request.form:
            act_link = generate_verification_link(user_id)
            message = Message("Activate your account", 
                sender=("ReX", app.config['MAIL_USERNAME']))
            user = get_user(user_id)
            message.recipients = [ user['user_email'] ]
            message.html = render_template("email_activation.html.j2", act_link=act_link)
            try:
                mail.send(message)
            except smtplib.SMTPRecipientsRefused:
                flash('e-mail address not accepted by this server')
            except Exception as ex:
                flash("Something has gone terribly wrong")
                app.logger.error('Verification mail error "{}"'.format(ex))

    user = get_user(user_id)
    mailserver = False
    if app.config['MAIL_SERVER'] != None and app.config['MAIL_SERVER'] != '':
        mailserver = True
    return render_template('profile.html.j2', user=user, mailserver=mailserver)

@app.route('/activate/<string:activation_code>')
def activate_email(activation_code):
    try:
        if verify_user_email(activation_code):
            flash("User has been activated")
            return redirect(url_for("homepage"))
    except Exception as ex:
        app.logger.error('Elegant activate check')
    
    flash("Could not activate user")
    return redirect(url_for("homepage"))

@app.route('/content')
@login_required
def content():
    all_content = get_content()
    return render_template('content.html.j2', all_content=all_content)
    