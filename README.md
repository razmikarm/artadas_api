# Artadas API

API server for Artadas project


## Setup Instructions

### Prerequisites

- Python 3.12+
- Docker
- [Docker Compose](https://docs.docker.com/compose/install/linux/#install-using-the-repository) plugin

### Initialization

1. Clone the repository:
   ```bash
   git clone --recurse-submodules git@github.com:razmikarm/artadas_api.git
   cd artadas_api
   ```

2. Rename `.env.example` to `.env` and fill real data (also for `auth` submodule)
   ```bash
   cp .env.example .env
   ```

### Local Installation and Run

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Access the API at [127.0.0.1:8000](http://127.0.0.1:8000).

5. View the interactive API docs:
   - Swagger UI: [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)


### Run with Docker

> Before running any docker command navigate to `docker` directory
> Make sure you have SSL certificates in `nginx/certs` directory 

1. Navigate to `docker` directory
   ```bash
   cd docker
   ```

2. Update write permission on init script
   ```bash
   chmod a+w init-scripts/02_init-auth-db.sql
   ```

3. Build your containers:
   ```bash
   docker compose build
   ```

4. Run containers:
   ```bash
   docker compose up
   ```

5. Access the API at [0.0.0.0:8000](http://0.0.0.0:8000).

6. View the interactive API docs:
   - Swagger UI: [0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)
   - ReDoc: [0.0.0.0:8000/redoc](http://0.0.0.0:8000/redoc)

> The project will be mounted in container and will reload on new changes


## Development

### Add pre-commits

1. Install Pre-Commit Hooks:
   ```bash
   pre-commit install
   ```

2. Check if it's working:
   ```bash
   pre-commit run --all-files
   ```

### Check code manually

1. Run to check with linter:
   ```bash
   ruff check
   ```

2. Run to resolve fixable errors:
   ```bash
   ruff check --fix
   ```

3. Run to reformat code:
   ```bash
   ruff format
   ```

### Manage migrations

> To only start database service, run `docker compose up db` 

1. Generate new revision:
   ```bash
   alembic revision --autogenerate -m "Your migration message"
   ```

2. Upgrade Database with new revision:
   ```bash
   alembic upgrade head
   ```

### Update submodule

1. When main repository detects that the submodule's commit reference has changed
   ```bash
   git add <auth or tg_bot>
   git commit -m "Updated <Auth or TG_Bot> submodule to the latest version"
   ```

2. Update submodules to the latest commit that repositories references
   ```bash
   git submodule update --remote
   ```


### Clean container dev database

1. Remove existing containers
   ```bash
   docker compose down
   ```

2. Remove database volume
   ```bash
   docker volume rm artadas_api_postgres_data
   ```

3. Or delete volumes with one command:
   ```bash
   docker-compose down -v
   ```


## Testing

1. Install testing dependencies:
   ```bash
   pip install pytest pytest-asyncio
   ```

2. Run tests:
   ```bash
   pytest
   ```

---

### Future Enhancements
- Add authentication using OAuth2 or JWT.
- Integrate Alembic for database migrations.
- Deploy to a cloud provider like AWS, GCP, or Heroku.
