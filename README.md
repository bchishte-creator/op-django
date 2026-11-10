# OST Food Tracker

The OST Food Tracker is a Django application for recording team members' food events and then searching, viewing, and sharing those events through web pages and a REST API. It was built as an onboarding project. This README describes what exists, how the parts fit together, how to run it, and which onboarding tasks remain.

## Project status

| Onboarding part | Status | What is included / what remains |
|---|---|---|
| Part 1: Application bones | Complete | Django project and app, six page templates, navigation, responsive styling, and local mockup photos. |
| Part 2: Data model and database | Implemented | Normalized Django models, migrations, database-backed submission and search, photo uploads, and PostgreSQL support. The developer setup described below has been migrated to PostgreSQL and populated from the SQLite fixture. |
| Part 3: REST API | Implemented | Django REST Framework CRUD endpoints for categories, people, foods, and food events, including search and filters. |
| Part 4: Containerize | Complete locally | Docker Compose runs Django/Gunicorn, PostgreSQL, and Nginx with persistent database/static/media volumes. The app was verified at `http://localhost:8080`, including login, displayed images, and recipe submission. |
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
- Docker Engine and Docker Compose for Part 4.
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

## Run the containerized app (Part 4)

Docker Compose starts its own PostgreSQL container and database volume. This database is separate from both the SQLite `db.sqlite3` file and any PostgreSQL server installed directly on your computer. The Django container runs migrations on startup; named volumes preserve the container database and uploaded files when containers stop.

Create a local `.env` file from the example. `.env` is ignored by Git; do not commit real passwords or secret keys:

```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Edit `.env` and set a unique, strong value for both `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY` (you can use the generated value for the secret key). Leave the example empty values out; Compose will refuse to start until both are set.

Start the application from the project directory:

```bash
docker compose up --build
```

Open <http://localhost:8080/>. Django Admin is at <http://localhost:8080/admin/>, and the REST API is at <http://localhost:8080/api/>. In another terminal, create demo records or an admin user:

```bash
docker compose exec web python manage.py seed_demo_data
docker compose exec web python manage.py createsuperuser
```

To check the services and logs:

```bash
docker compose ps
docker compose logs -f web nginx
```

Stop the containers with `Ctrl+C`, then run `docker compose down`. The named volumes are kept. To start again use `docker compose up`; do not use `docker compose down -v` unless you deliberately want to permanently delete the container database and uploaded files.

The Nginx port is bound to `127.0.0.1` only, so this Compose setup is for local development and is not publicly reachable by default. It runs with `DEBUG=False`, uses Gunicorn behind Nginx, and serves static and uploaded media files from shared volumes. The training API is still unauthenticated, so do not expose this setup to an untrusted network.

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

## Onboarding hand-off checklist

These are the sharing, review, or presentation items explicitly called out in the onboarding assignment. Checking a box is a coordination task outside the codebase; having the document in this repository does not mean it has been shared.

- [ ] **Part 1 — mockups:** Share the page mockups with your manager or a team lead. The current mockup images came from the provided project materials; confirm whether your lead expects a separate presentation of your implemented pages as well.
- [ ] **Part 2 — data model and backend:** Share the normalized ER diagram in [docs/DATA_MODEL.md](docs/DATA_MODEL.md) with your manager or a team lead, and present the implemented schema and database-backed insertion/search pages.
- [ ] **Part 3 — REST API:** Share [docs/API.md](docs/API.md) with your manager or a team lead, and walk them through the API endpoints. A quick local demo is available at `/api/` and `/api/events/` when the development server is running.
- [ ] **Part 3 — API behavior demo:** Demonstrate how API clients can read and create records (and, if useful, update/delete them), as well as search/filter food events.

The onboarding instructions do not specify a separate manager/team-lead hand-off for Parts 4 or 5. Their implementation deliverables are tracked below.

## Remaining implementation work

1. **Part 4 — containerization:** Complete locally. Docker Compose started Django/Gunicorn, PostgreSQL, and Nginx; the user confirmed login, displayed images, and recipe submission work at `localhost:8080`. Review the configuration with your team if required.
2. **Part 5 — deployment (not started):** With the required UNH/IOL infrastructure access, provision a VM on the OS Infrastructure network, join it to OS IPA, create the HTTP service principal, request a certificate with `ipa-getcert`, and configure Nginx to serve HTTPS and redirect HTTP to HTTPS.

Parts 1–3 are implemented in code. The Part 1–3 sharing/presentation items above still need to be done with your manager or team lead. Part 4's local Compose stack is implemented and working. Part 5 is not implemented. The Django development server (`runserver`) is for local development only and is not the server used by Compose or the eventual production deployment.
