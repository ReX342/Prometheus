
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