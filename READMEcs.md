# Prometheus' Trashfire
#### Video Demo:  https://youtu.be/Gq8117wWSBk
#### Description:

Do you post too many memes in discord for your friends to keep up?
I do, so I made a discord bot named Prometheus.
He scrapes the #stream-of-consciousness channel on my Discord Server using an implementation of discordbot python
Requirements: Server access to my discord server

I made a website in Flask that allows users to vote posts up or down and provided pages to register and log in and out.
I implemented dynamically generated HTML image tags in Python using Jinja templating to correctly render images from posts.
I embedded tweets using the JavaScript snippet Twitter provides.
I provided infinite scroll functionality (even though that’s unethical) and a page to show a random post.

For the most recent version of the project, check out: https://github.com/ReX342/Prometheus
This is a web-based application using JavaScript, Python, and SQL, based in part on the web track’s distribution code

##### Technical details:
###### Two Readme's
#### Readme.md from discordbot (input):
First we make a virtual environment:
```
python -m venv venv
```
Secondly, we activate said environment:
```
.\venv\Scripts\activate.ps1
```
Now, we can install all pip dependencies
```
pip install -r requirement.txt
```
Insert your Token in our bot's file (here: Prometheus.py)
This can be found at the 'Bot' tab in your discord's developer portal
For more information and screenshots on where to find this in your GUI, consult the original:
    https://realpython.com/how-to-make-a-discord-bot-python/

Prometheus only checks the channel named #stream-of-consciousness. Adapt as you see fit (or make a namesake channel)

We'll have to configure access to our Discord developper TOKEN.
    https://discord.com/developers/applications
(You'll have made a TOKEN following the realpython URL above)
(Bot -> click 'copy' beneath TOKEN)
Put this TOKEN in your .env file:
    TOKEN=youractualtoken
Be sure you don't use spaces or airquotes.

Now we have to keep this running so it can add content to our database:
    python .\Prometheus.py

You'll notice a database (.db) has been created upon running Prometheus.

Now follow the readme.md of the website that'll be hosting your content.

Code of conduct:
    Do one thing.
    More will follow at an appropriate time.

#### Readme for the website (output)

# Flask Project

### If you are only interested in running the source code

(for windows: Visual Studio Code powershell terminal)

```powershell
git clone https://github.com/ReX342/Prometheus
cd Prometheus
python -m venv venv
& '.\venv\Scripts\activate.ps1'
pip install -r requirements.txt
flask run
```

If it fails, it'll tell you to run the following line, then just continue as you were

```
python -m pip install --upgrade pip
pip install -r requirements.txt
flask run
```

Define a `.flaskenv` file with the following options.

```sh
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY="for-dev-environment-only"
MAIL_SERVER=""
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=""
MAIL_PASSWORD=""
```

## Running

```
& '.\venv\Scripts\activate.ps1'
flask run
```