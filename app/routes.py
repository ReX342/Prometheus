from app import app
from app import mail
from app.database import *
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from functools import wraps
from flask_mail import Message
import smtplib
import re

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
                # Enter your own username here as sender
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

@app.route('/tweets')
@login_required
def tweets():
    all_content = get_content()
    tweet_ids = []
    for message in all_content:
        message = message[0]
        matches = re.findall("https?://twitter.com/[^\s]*/(\d+)", message)
        tweet_ids += matches
    return render_template('tweets.html.j2', tweet_ids=tweet_ids)

@app.route('/attachment')
@login_required
def attachment():
    all_attachments = get_attachment()
    return render_template('attachment.html.j2', all_attachments=all_attachments)

# from https://github.com/sir-ragna/pagination/ opting not to use unethical infinite scroll

# Secretkey needed for discordbot?
@app.route('/pages/<int:page>')
@login_required
def pagination(page):
    if page == 0:
        app.logger.error("page is 0 and it shouldn't be!")
        page = 1
    amount = 5
    offset = (page - 1) * amount
    posts = get_posts_offset_based(offset=offset, amount=amount)
    nextpage = page + 1
    previouspage = page - 1
    return render_template('pagination.html.j2', posts=posts, 
        nextpage=nextpage, previouspage=previouspage)
    
@app.route('/random')
@login_required
def random():
    random_posts = get_random()     
    return render_template('random.html.j2', random_posts=random_posts)

@app.route('/dashboard')
@login_required
def dashboard():
    random_posts = get_random(number_posts=100)     
    return render_template('dashboard.html.j2', random_posts=random_posts)
   
@app.route('/inferno')
@login_required
def inferno():
    timestamp = request.args.get('cursor')
    if timestamp == None:
        timestamp = datetime.utcnow().isoformat()
    posts, last_post_timestamp = get_posts_cursor_based(timestamp)

    # Handle request from javascript
    if request.content_type == 'application/json':
        posts = [post.toDict() for post in posts]
        return jsonify(posts), 200
    
    return render_template('inferno.html.j2', posts=posts, cursor=last_post_timestamp)

@app.route('/random_tweets')
@login_required
def random_tweets():
    # all_random_tweets = get_random_tweets
    random_posts = get_random_tweet()     
    # all_content = get_content()
    tweet_ids = []
    for message in random_posts:
        message = message[0]
        matches = re.findall("https?://twitter.com/[^\s]*/(\d+)", message)
        tweet_ids += matches
    return render_template('random_tweets.html.j2', tweet_ids=tweet_ids)

@app.route('/attach_ratings')
@login_required
def attach_ratings():
    usr_id = session['user_id']
    random_posts = get_random()     
    return render_template('attach_ratings.html.j2', usr_id = usr_id, random_posts=random_posts)

@app.route('/vote', methods=['POST', 'GET'])
@login_required
def vote():
    rated = request.args.get('value')
    print(rated)
    attachment_id = request.args.get('attachment_id')
    try:
        insert_vote(session['user_id'], attachment_id, rated)
        return "", 200
    except Exception as ex:
        app.logger.error("{}".format(ex), exc_info=True)
         