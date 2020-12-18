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