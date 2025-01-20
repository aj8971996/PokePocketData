# PokéPocketData

## Description
A comprehensive Angular application for managing and analyzing Pokémon data. This project is developed for personal learning and practice purposes, designed to run locally. It aims to provide users with an intuitive interface to explore, analyze, and manage Pokémon information while implementing best practices in full-stack development.

## Features (Planned)
- Comprehensive Pokémon database integration with MySQL
- Interactive data visualization
- Advanced search and filtering capabilities
- Responsive design for mobile and desktop platforms
- Real-time data updates and synchronization
- Implementation of proper database modeling and relationships

## Technical Stack

### Frontend
- Angular (Frontend Framework)
- TypeScript
- HTML5/CSS3
- Additional frontend libraries will be listed as integrated

### Backend
- Python (API Development)
- FastAPI (Python Web Framework)
- MySQL 8.0 (Database)
- SQLAlchemy (ORM)
- Alembic (Database Migrations)
- Python-dotenv (Environment Management)
- Additional backend libraries listed in requirements.txt

### Development Tools
- Git for version control
- MySQL Workbench
- Additional development tools will be listed as needed

## Prerequisites
- Node.js 
- npm
- Angular CLI
- Python 3.8+ 
- pip
- Git
- MySQL Server 8.0
- MySQL Workbench

## Database Setup

### MySQL Installation and Configuration
1. Install MySQL Server 8.0 and MySQL Workbench
2. Create a new connection in MySQL Workbench:
   - Connection Name: PokePocketData_Local
   - Hostname: localhost
   - Port: 3306
   - Username: ppdd_api_user (create this user for API connections)

3. Set up the API user with appropriate permissions:
```sql
CREATE USER 'ppdd_api_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON pokepocketdata.* TO 'ppdd_api_user'@'localhost';
FLUSH PRIVILEGES;
```

### Environment Configuration
1. Create a `.env` file in the backend directory:
```plaintext
DB_USER=ppdd_api_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
```

Note: Never commit the `.env` file to version control. A `.env.example` template is provided for reference.

## Installation

### 1. Repository Setup
```bash
git clone https://github.com/[your-username]/PokePocketData.git
cd PokePocketData
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Backend Setup
```bash
cd ../backend
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Initialization
```bash
# Initialize the database and create tables
python -m app.database.base

# Initialize Alembic for migrations
alembic init migrations

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 5. Start the Application
```bash
# Start the backend server (from backend directory)
uvicorn app.main:app --reload

# Start the frontend development server (from frontend directory)
ng serve
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Project Structure
```
PokePocketData/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Database connection and initialization
│   │   │   ├── config.py        # Database configuration
│   │   │   └── models.py        # SQLAlchemy models
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── ppdd_models.py   # Pydantic models for API
│   │   ├── routers/
│   │   ├── services/
│   │   └── utils/
│   ├── .env                     # Environment variables
│   └── requirements.txt
└── frontend/
    └── [Angular project files]
```

## Database Models
The project implements two types of models:
1. SQLAlchemy Models (`app/database/models.py`):
   - Define database table structures
   - Handle relationships and constraints
   - Manage database operations

2. Pydantic Models (`app/models/ppdd_models.py`):
   - Handle API request/response validation
   - Manage data serialization
   - Implement business logic validation

## Development Status
🚧 The project is currently in the initial setup phase, with the following completed:
- Basic project structure
- Database models defined (both SQLAlchemy and Pydantic)
- Database connection configuration with environment variables
- Migration system setup with Alembic
- Initial API user setup

## Local Development Notes
- This project is designed for local development and learning purposes
- Database connections are configured for localhost only
- Environment variables should be set up locally using the provided `.env.example` template
- API user (ppdd_api_user) is configured with local-only permissions
- Database migrations are handled through Alembic

## Contributing
As this is a personal development project, contributions are currently not being accepted. Feel free to fork the repository for your own learning purposes.

## Troubleshooting

### Common Issues
1. Database Connection Errors:
   - Verify MySQL service is running
   - Check credentials in `.env` file
   - Ensure ppdd_api_user has proper permissions

2. Migration Issues:
   - Clear any existing migrations: `alembic downgrade base`
   - Remove migration versions directory
   - Reinitialize: `alembic init migrations`
   - Create new migration: `alembic revision --autogenerate`

---
**Note:** This README will be updated as the project evolves and new features are implemented.