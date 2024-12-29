# Artadas API

API server for Artadas project

## Setup Instructions

### Prerequisites
- Python 3.12+
- pip

### Intialization
1. Clone the repository:
   ```bash
   git clone git@github.com:razmikarm/artadas_api.git
   cd artadas_api
   ```
2. Rename `.env.example` to `.env` and fill real data 

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
2. Access the API at `http://127.0.0.1:8000`.
3. View the interactive API docs:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

### Run with Docker

1. Install Docker in your system
2. Install the [Docker Compose](https://docs.docker.com/compose/install/linux/#install-using-the-repository) plugin

3. Build your containers:
```bash
docker compose build
```

4. Run containers:
```bash
docker compose up
```

 > The project will be mounted in container, so that container will be up-to-date and will reload on new changes
---

### Linter

1. Run to check code formatting:

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

---
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

## Future Enhancements
- Add authentication using OAuth2 or JWT.
- Integrate Alembic for database migrations.
- Deploy to a cloud provider like AWS, GCP, or Heroku.
