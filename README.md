# PokéPocketData

## Description
A comprehensive web application for managing and analyzing Pokémon card game data. This project is developed for personal learning and practice purposes, designed to run locally. It aims to provide users with an intuitive interface to explore, analyze, and manage Pokémon card game information while implementing best practices in full-stack development.

## Features (Implemented/Planned)
- ✅ Comprehensive Pokémon card database integration with MySQL
- 🚧 Interactive data visualization
- 🚧 Advanced search and filtering capabilities
- 🚧 Responsive design for mobile and desktop platforms
- ✅ Implementation of proper database modeling and relationships
- ✅ RESTful API with FastAPI
- ✅ Type-safe data validation using Pydantic
- ✅ Comprehensive game record tracking
- 🚧 Deck management and analysis

## Current Implemented Components
- Database Models
  - Card Management (Pokémon and Trainer Cards)
  - Deck Management
  - Game Record Tracking
- API Endpoints for:
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

## Database Setup

### MySQL Configuration
1. Install MySQL Server 8.0 and MySQL Workbench
2. Create a new MySQL user for the application:
```sql
CREATE USER 'ppdd_api_user'@'localhost' IDENTIFIED BY 'your_password';
CREATE DATABASE pokepocketdata;
GRANT ALL PRIVILEGES ON pokepocketdata.* TO 'ppdd_api_user'@'localhost';
FLUSH PRIVILEGES;
```

### Environment Configuration
Create a `.env` file in the backend directory:
```plaintext
DB_USER=ppdd_api_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
```

## Installation

### 1. Clone the Repository
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
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
# On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Initialization
```bash
# Initialize the database and create tables
python -m app.database.base

# Create and apply database migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Start the Application
```bash
# Start the backend server (from backend directory)
uvicorn app.main:app --reload

# Start the frontend development server (from frontend directory)
ng serve
```

## Project Structure
```
PokePocketData/
├── backend/
│   ├── app/
│   │   ├── database/           # Database configuration and models
│   │   ├── models/             # Pydantic models and schemas
│   │   ├── routers/            # API endpoint definitions
│   │   ├── services/           # Business logic services
│   │   └── utils/              # Utility functions
│   ├── .env                    # Environment configuration
│   └── requirements.txt        # Python dependencies
└── frontend/                   # Angular application
    └── [Angular project files]
```

## API Capabilities
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

### In Progress
- 🚧 Frontend implementation
- 🚧 Advanced data visualization
- 🚧 Comprehensive test coverage

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