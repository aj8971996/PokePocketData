# PokéPocketData

## Description
A comprehensive web application for managing and analyzing Pokémon card game data. This project is developed for personal learning and practice purposes, designed to run locally. It aims to provide users with an intuitive interface to explore, analyze, and manage Pokémon card game information while implementing best practices in full-stack development.

## Features (Implemented/Planned)
- ✅ Comprehensive Pokémon card database integration with MySQL
- ✅ Google OAuth authentication system
- 🚧 Interactive data visualization
- 🚧 Advanced search and filtering capabilities
- 🚧 Responsive design for mobile and desktop platforms
- ✅ Implementation of proper database modeling and relationships
- ✅ RESTful API with FastAPI
- ✅ Type-safe data validation using Pydantic
- ✅ Comprehensive game record tracking
- 🚧 Deck management and analysis

## Current Implemented Components
- Authentication System
  - Google OAuth 2.0 Integration
  - JWT Token Management
  - Protected Routes
- Database Models
  - User Management
  - Card Management (Pokémon and Trainer Cards)
  - Deck Management
  - Game Record Tracking
- API Endpoints for:
  - Authentication
  - Card Creation and Retrieval
  - Deck Creation and Management
  - Game Record Logging
  - Player Statistics

## Technical Stack

### Frontend
- Angular (Frontend Framework)
- TypeScript
- HTML5/CSS3

### Backend
- Python 3.8+
- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- MySQL 8.0 (Database)
- Alembic (Database Migrations)
- Python-dotenv (Environment Management)
- JWT Authentication
- Google OAuth 2.0

### Development Tools
- Git (Version Control)
- MySQL Workbench
- Visual Studio Code

## Prerequisites
- Node.js 16+ 
- npm
- Angular CLI
- Python 3.8+ 
- pip
- Git
- MySQL Server 8.0
- MySQL Workbench
- Google Cloud Platform Account (for OAuth)

## Setup Instructions

### 1. Google OAuth Configuration
1. Create a project in Google Cloud Console
2. Enable Google OAuth API
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials (Web application)
5. Note your Client ID and Client Secret

### 2. Environment Configuration
Create a `.env` file in the backend directory:
```plaintext
DB_USER=ppdd_api_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_secure_jwt_secret
```

### 3. Database Setup
```sql
CREATE USER 'ppdd_api_user'@'localhost' IDENTIFIED BY 'your_password';
CREATE DATABASE pokepocketdata;
GRANT ALL PRIVILEGES ON pokepocketdata.* TO 'ppdd_api_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Installation Steps
```bash
# Clone repository
git clone https://github.com/[your-username]/PokePocketData.git
cd PokePocketData

# Frontend setup
cd frontend
npm install

# Backend setup
cd ../backend
python -m venv venv
source venv/bin/activate  # Unix/macOS
# On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Initialize database and migrations
python -m app.database.base
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Starting the Application
```bash
# Start backend server (from backend directory)
uvicorn app.main:app --reload

# Start frontend server (from frontend directory)
ng serve
```

## Project Structure
```
PokePocketData/
├── backend/
│   ├── app/
│   │   ├── database/           # Database configuration and models
│   │   │   ├── base.py        # Database initialization
│   │   │   ├── db_config.py   # Database configuration
│   │   │   └── sql_models.py  # SQLAlchemy models
│   │   ├── models/            # Pydantic models and schemas
│   │   ├── routers/           # API endpoint definitions
│   │   │   ├── auth.py       # Authentication routes
│   │   │   └── ppdd_router.py # Main application routes
│   │   ├── services/          # Business logic services
│   │   └── utils/            # Utility functions
│   ├── logs/                 # Application logs
│   ├── .env                  # Environment configuration
│   └── requirements.txt      # Python dependencies
└── frontend/                 # Angular application
    ├── src/
    │   ├── app/
    │   │   ├── auth/         # Authentication components
    │   │   ├── core/         # Core components
    │   │   └── features/     # Feature modules
    │   └── assets/
    │       └── images/       # Static images including logo
    └── [Angular project files]
```

## API Capabilities
- Authentication:
  - Google OAuth 2.0 Login
  - JWT Token Management
- Full CRUD operations for:
  - Pokémon Cards
  - Trainer Cards
  - Decks
  - Game Records
- Advanced filtering and pagination
- Comprehensive data validation
- Game statistics tracking
- Health check endpoint

## Development Status
🚧 **Current Status: Active Development**

### Completed
- ✅ Database modeling
- ✅ API endpoint implementation
- ✅ Basic data validation
- ✅ Game record tracking
- ✅ Authentication system

### In Progress
- 🚧 Frontend implementation
- 🚧 Advanced data visualization
- 🚧 Comprehensive test coverage

[Rest of the sections remain the same...]

## Troubleshooting

### Common Issues
1. **Database Connection**
   - Verify MySQL is running
   - Check `.env` credentials
   - Ensure `ppdd_api_user` has proper permissions

2. **Migration Problems**
   ```bash
   # Reset migrations if needed
   alembic downgrade base
   alembic revision --autogenerate -m "Reset migration"
   alembic upgrade head
   ```

3. **API Debugging**
   - Check FastAPI logs
   - Verify request payloads
   - Ensure database connection

## Future Roadmap
- Implement comprehensive frontend
- Add authentication system
- Develop advanced analytics
- Create user management
- Implement deck building tools
- Add tournament tracking features

## Contributing
This is a personal learning project. While contributions are not currently accepted, feel free to fork and learn from the codebase.

## License
[To be added - include your chosen license]

---
**Note:** Project is under active development and documentation will be continuously updated.