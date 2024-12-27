# Artadas API

API server for Artadas project

## Setup Instructions

### Prerequisites
- Python 3.12+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone git@github.com:razmikarm/artadas_api.git
   cd artadas_api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Run the Application
1. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Access the API at `http://127.0.0.1:8000`.
3. View the interactive API docs:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

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
