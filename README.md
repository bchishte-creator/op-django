# OST Food Tracker

A Django food-tracking project with database-backed event entry, search, a photo gallery, and a REST API. Its normalized model and API endpoints are documented in [docs/DATA_MODEL.md](docs/DATA_MODEL.md) and [docs/API.md](docs/API.md). The provided UNH Interoperability Labs logo is saved at `tracker/static/tracker/images/our-logo.png` and used in the shared navigation and login page.

## Run locally with SQLite

SQLite is the default for getting started; PostgreSQL setup is below.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. The `seed_demo_data` command creates sample people, categories, meals, and local photos so the pages are populated. You can run it again safely without duplicating those sample events.

## Use PostgreSQL

Install and start PostgreSQL, then create the application's database user and database:

```bash
sudo apt install postgresql
sudo -u postgres createuser --pwprompt ost_food_tracker
sudo -u postgres createdb --owner=ost_food_tracker ost_food_tracker
```

Set the connection settings in the same terminal where you run Django. Use the password you entered for `createuser`:

```bash
export DATABASE_ENGINE=postgresql
export DB_NAME=ost_food_tracker
export DB_USER=ost_food_tracker
export DB_HOST=localhost
export DB_PORT=5432
read -s -p "PostgreSQL password: " DB_PASSWORD; echo; export DB_PASSWORD
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

`psycopg` is included in `requirements.txt`. PostgreSQL settings are selected only when `DATABASE_ENGINE=postgresql`; otherwise Django uses the local SQLite database.

## Pages and API

- Pages: Home (`/`), Submit (`/submit/`), Search (`/search/`), Food Pictures (`/food-pictures/`), About (`/about/`), and Login (`/login/`).
- API: `/api/` lists resources; CRUD endpoints are documented in [docs/API.md](docs/API.md).
- Django admin: `/admin/`.
- Uploaded event photos are stored in the local `media/` directory during development.

Use **Login** with the Django username and password you created (for example with `python manage.py createsuperuser`). The email address is not the login name. The training API is unauthenticated as the assignment specifies, so do not expose it to untrusted networks.

## Run tests

```bash
python manage.py test
```
