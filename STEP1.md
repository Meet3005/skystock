# SkyStock — checkpoint 1

This checkpoint provides a Flask API and PostgreSQL database for local development.
It does not yet implement inventory management, login, or a React interface.

## Add to your repository

Copy `backend`, `compose.yaml`, and this file into your existing `skystock`
repository. Keep the existing `.git`, `.gitignore`, and `README.md`.
Do not place the whole `skystock-step1` folder inside the repository.

## Start

Keep Docker Desktop running. Open the repository in VS Code and choose
Terminal > New Terminal. From the repository root run:

```sh
docker compose up --build -d
docker compose ps
```

The first run downloads Python and PostgreSQL images and installs the two Python
dependencies. The API waits for PostgreSQL's readiness check before starting.

Open http://localhost:8000/api/health in your browser. Expected HTTP 200 response:

```json
{"app":"SkyStock","database":"connected","status":"ok"}
```

The root page, http://localhost:8000/, is also JSON. There is no visual interface yet.

## Understand the files

* `backend/app.py` defines the HTTP endpoints. `/api/health` actually queries the
  database with `SELECT 1`; it returns HTTP 503 if the database cannot be reached.
* `backend/requirements.txt` pins the Python dependencies for this checkpoint.
* `backend/Dockerfile` defines the Python container and its startup command.
* `compose.yaml` connects the two containers. The hostname `db` resolves to the
  PostgreSQL container inside the Compose network.
* The named volume `skystock_data` keeps database files when containers stop or
  are recreated. It is not a backup.

## Troubleshooting

```sh
docker compose ps
docker compose logs --tail=60 api db
```

If a terminal reports no Compose configuration file, navigate to the repository
folder containing `compose.yaml`.

## Stop

```sh
docker compose down
```

This preserves the database volume. Do not add `-v` unless you intend to erase
the local database.

## Scope and verification

This is a local development checkpoint. It uses Flask's development server,
a local example database password, and a localhost-only published API port.
Before AWS deployment we will add a production server, proper secrets, HTTPS,
authentication, and backups.

The delivery environment did not provide Docker. Python syntax and configuration
structure passed checks. HTTP checks passed for the root route, missing configuration,
database failure without credential disclosure, and a successful query using a mock
database. The actual
container build, image downloads, ARM compatibility, and live PostgreSQL connection
must be verified with the commands above on your Mac.
