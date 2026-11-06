# OST Food Tracker

The OST Food Tracker is a Django application for recording team members' food events and then searching, viewing, and sharing those events through web pages and a REST API. It was built as an onboarding project. This README describes what exists, how the parts fit together, how to run it, and which onboarding tasks remain.

## Project status

| Onboarding part | Status | What is included / what remains |
|---|---|---|
| Part 1: Application bones | Complete | Django project and app, six page templates, navigation, responsive styling, and local mockup photos. |
| Part 2: Data model and database | Implemented | Normalized Django models, migrations, database-backed submission and search, photo uploads, and PostgreSQL support. The developer setup described below has been migrated to PostgreSQL and populated from the SQLite fixture. |
| Part 3: REST API | Implemented | Django REST Framework CRUD endpoints for categories, people, foods, and food events, including search and filters. |
| Part 4: Containerize | Not started | Add a production WSGI server (for example Gunicorn), Nginx, Dockerfiles and Docker Compose for Django/PostgreSQL/Nginx, and shared static/media volumes. The Compose site should be available on `localhost:8080`. |
| Part 5: Deploy | Not started | Deploy to an approved UNH/IOL VM, join it to the OS IPA domain, request and configure the HTTP TLS certificate, and serve HTTPS through Nginx with HTTP redirected to HTTPS. This requires access to the organization's infrastructure. |

Part 2's code is implemented and PostgreSQL is supported. The project still defaults to SQLite if PostgreSQL environment variables are not set in the current terminal; see [Database selection](#database-selection). Sharing the ER diagram and API documentation with a manager or team lead is also a project follow-up.

## What the application does

- **Home** shows database-backed event totals, this week's count, the most-used category, and recent meals.
- **Submit** lets a user record a food, team member, category, date/time, notes, and optional photo.
- **Search** filters events by food/person/category/notes, category, and date period.
- **Food Pictures** displays uploaded event photos.
- **About** describes the project.
- **Login / Logout** use Django's built-in session authentication. Create accounts with Django's user commands or admin; the email address is not the login name.
- **Django Admin** provides a separate staff interface to manage accounts and tracker records.
- **REST API** exposes the same tracker data to other programs as JSON.

### Request and data flow

```text
Browser page form ──> tracker URL ──> Django view/form ──> Django ORM ──> PostgreSQL or SQLite
Browser/API client ──> /api/ ───────> DRF viewset/serializer ──> Django ORM ──> same database
```

The Django ORM is the application's database interface. It maps the Python models to relational tables and turns queries into SQL for the configured database. Django Admin, the HTML pages, and the REST API all read and write through that same ORM. PostgreSQL does not provide the Django Admin screen; it stores the tables and rows, which can also be inspected with `psql` or a database client such as pgAdmin or DBeaver.

Uploaded food photos are files on disk under `media/`; the database stores each photo's relative file path. The provided UNH Interoperability Labs logo and static food examples live under `tracker/static/tracker/images/`.

## Data model

The normalized schema has four tables:

- **Food** stores each food name once.
- **TeamMember** stores each team member once.
- **Category** stores each category once.
- **FoodEvent** links a food, consumer, and category to a date/time, notes, and optional photo.

This avoids repeating food, person, and category names in every event row. See [docs/DATA_MODEL.md](docs/DATA_MODEL.md) for the ER diagram, relationships, and normalization notes. The migration that creates the tables is [tracker/migrations/0001_initial.py](tracker/migrations/0001_initial.py).

## Project layout

```text
food_tracker/                 Django project configuration and root URLs
tracker/
  models.py                   Database tables and relationships
  forms.py                    Submit and search form validation
  views.py                    HTML page request handling and ORM queries
  urls.py                     HTML page routes
  api.py                      REST API viewsets
  api_urls.py                 REST API routes
  serializers.py              JSON input/output definitions
  admin.py                    Django Admin configuration
  migrations/                 Versioned database schema changes
  templates/tracker/          Shared layout and page templates
  static/tracker/             CSS, logo, and bundled sample images
  management/commands/        seed_demo_data command
docs/
  DATA_MODEL.md               ER diagram and schema explanation
  API.md                      API endpoint reference
manage.py                     Django command-line entry point
requirements.txt              Python package dependencies
```

## Requirements

- Python 3.14 (or a Python version compatible with the installed Django dependencies)
- PostgreSQL for the Part 2 relational database requirement; SQLite remains available for a quick local start.
- For the API, photo uploads, and PostgreSQL support: the packages listed in `requirements.txt`.

## Run locally

Create and activate a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Quick start with SQLite

SQLite is selected by default when `DATABASE_ENGINE` is unset. From the project directory:

```bash
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Visit <http://127.0.0.1:8000/>. The admin is at <http://127.0.0.1:8000/admin/>. Create a Django admin account with:

```bash
python manage.py createsuperuser
```

The demo-data command creates sample categories, people, food events, and photos. It is safe to run again; existing demo events will not be duplicated.

## Use PostgreSQL

PostgreSQL is the database backend required by Part 2. Install and start PostgreSQL if needed, then create the application's role and database (omit `sudo apt install postgresql` if you already installed it):

```bash
sudo apt install postgresql
sudo -u postgres createuser --pwprompt ost_food_tracker
sudo -u postgres createdb --owner=ost_food_tracker ost_food_tracker
```

If the role or database already exists, do not repeat creation blindly; continue with the existing role/database. Set these environment variables in the same terminal where you run Django. Enter the password chosen for the PostgreSQL role:

```bash
export DATABASE_ENGINE=postgresql
export DB_NAME=ost_food_tracker
export DB_USER=ost_food_tracker
export DB_HOST=localhost
export DB_PORT=5432
read -s -p "PostgreSQL password: " DB_PASSWORD; echo; export DB_PASSWORD
```

Then create the schema and optionally load sample records:

```bash
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Check which backend Django is using:

```bash
python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
```

For PostgreSQL this should report `postgresql ost_food_tracker`. `DATABASE_ENGINE` and `DB_*` are shell environment variables; a new terminal does not inherit them automatically. Set them again there before running Django, or Django will use the default SQLite file.

### SQLite and PostgreSQL are separate

Selecting PostgreSQL does not delete or automatically copy `db.sqlite3`. Each database has its own tables and data. `migrate` creates tables in the currently selected database; it does not transfer records.

To copy tracker records from SQLite to PostgreSQL, export while SQLite is selected, then switch to PostgreSQL and import:

```bash
# SQLite selected: export tracker records to the parent folder.
python manage.py dumpdata tracker --indent 2 > ../ost-food-tracker-data.json

# After setting the PostgreSQL variables above:
python manage.py migrate
python manage.py loaddata ../ost-food-tracker-data.json
```

That fixture includes the tracker app's food data, not Django login accounts or the image files themselves. Create a PostgreSQL admin user separately with `python manage.py createsuperuser`. Copy the `media/` directory separately if you need the uploaded photos on another machine. Keep `db.sqlite3`, database credentials, and private uploads out of source control.

## Routes

### Web pages

| Page | URL |
|---|---|
| Home | `/` |
| Submit a food event | `/submit/` |
| Search food events | `/search/` |
| Food pictures | `/food-pictures/` |
| About | `/about/` |
| Login / Logout | `/login/` / `/logout/` |
| Django Admin | `/admin/` |

### REST API

The API root is `/api/`. Resources include categories, people, foods, and food events. Collection routes support `GET` and `POST`; item routes support `GET`, `PUT`, `PATCH`, and `DELETE`. Food-event search, filtering, date ranges, ordering, and example JSON requests are documented in [docs/API.md](docs/API.md).

**Training-only security note:** API write endpoints are intentionally unauthenticated to match the onboarding assignment. Do not expose this development configuration to an untrusted network or use it as-is in production.

## Tests and schema changes

Run the test suite and Django's configuration checks with:

```bash
python manage.py check
python manage.py test
```

After changing a model, create and apply a migration using the same database configuration that you intend to run:

```bash
python manage.py makemigrations
python manage.py migrate
```

Tests use Django's isolated temporary test database; they do not replace the development database.

## Remaining onboarding work

1. **Part 4 — containerization:** Add Docker Compose services for Django, PostgreSQL, Gunicorn (or another WSGI server), and Nginx. Configure Nginx to serve the site on `localhost:8080` and serve static and uploaded media files from shared volumes.
2. **Part 5 — deployment:** With the required UNH/IOL infrastructure access, provision a VM on the OS Infrastructure network, join it to OS IPA, create the HTTP service principal, request a certificate with `ipa-getcert`, and configure Nginx to serve HTTPS and redirect HTTP to HTTPS.
3. **Project hand-off:** Share the ER diagram and API endpoint documentation/demo with the manager or team lead, as required by Parts 2 and 3.

Parts 4 and 5 are not implemented in this repository yet. The Django development server (`runserver`) is for local development only and is not the production server required for those parts.
