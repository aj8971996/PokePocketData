# PokéPocketData

## Description

PokéPocketData is a comprehensive web application for managing and analyzing Pokémon Trading Card Game data. Built with a FastAPI backend and Angular frontend, this project demonstrates modern full-stack development practices with a focus on type safety, clean architecture, and robust data management. While developed primarily for learning purposes, it implements production-grade features including OAuth authentication, comprehensive API documentation, and thorough testing practices.

## Core Features

The application currently provides several key capabilities:

**Card Management System**
- Complete database of Pokémon and Trainer cards
- Detailed card attributes including abilities, types, and statistics
- Support for multiple card sets and pack types
- Advanced validation rules for card creation

**Authentication and Security**
- Google OAuth 2.0 integration
- JWT token management
- Protected routes and endpoints
- Role-based access control

**Game Management**
- Comprehensive game record tracking
- Player statistics and analysis
- Match history with detailed game data
- Point tracking and ranking system

**Deck Building**
- Support for 20-card deck construction
- Deck validation rules enforcement
- Card limit verification
- Deck statistics and analysis

## Technical Stack

**Backend Architecture**
- Python 3.10+
- FastAPI for API development
- SQLAlchemy 2.0 with async support
- MySQL 8.0 for data persistence
- Pydantic for data validation
- OAuth2 with Google authentication

**Frontend Framework**
- Angular 15+
- TypeScript
- Angular Material UI components
- RxJS for reactive programming

**Development Tools**
- Git for version control
- MySQL Workbench for database management
- Visual Studio Code as recommended IDE
- Comprehensive test suite using pytest

## Getting Started

### Prerequisites

Before setting up the project, ensure you have:
- Python 3.10 or higher
- Node.js 16 or higher
- MySQL 8.0
- Google Cloud Platform account
- Git

### Initial Setup

1. **Clone the Repository**
```bash
git clone https://github.com/[your-username]/PokePocketData.git
cd PokePocketData
```

2. **Configure Google OAuth**
- Create a project in Google Cloud Console
- Enable Google OAuth API
- Set up OAuth consent screen
- Create OAuth 2.0 credentials
- Note your Client ID and Secret

3. **Configure Environment**
Create `.env` in the backend/app/database directory:
```plaintext
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
JWT_SECRET=your_jwt_secret
```

4. **Database Setup**
```sql
CREATE DATABASE pokepocketdata;
CREATE USER 'ppdd_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON pokepocketdata.* TO 'ppdd_user'@'localhost';
FLUSH PRIVILEGES;
```

5. **Backend Installation**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.database.base
```

6. **Frontend Installation**
```bash
cd frontend
npm install
```

### Running the Application

**Start Backend Server**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend Development Server**
```bash
cd frontend
ng serve
```

Access the application at http://localhost:4200 and the API documentation at http://localhost:8000/api/docs

## Project Structure

```
PokePocketData/
├── backend/
│   ├── app/
│   │   ├── database/         # Database configuration and models
│   │   ├── models/          # Pydantic models
│   │   ├── routers/         # API endpoints
│   │   └── services/        # Business logic
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
└── frontend/              # Angular application (currently in development)
```

## Development Status

### Completed Features
- ✅ Comprehensive database modeling
- ✅ Complete API implementation with FastAPI
- ✅ Google OAuth integration
- ✅ JWT token management
- ✅ Card management system
- ✅ Game record tracking
- ✅ Deck management
- ✅ Advanced data validation
- ✅ Comprehensive test coverage for backend

### In Progress
- 🚧 Frontend implementation
- 🚧 Interactive data visualization
- 🚧 Advanced search functionality
- 🚧 Mobile-responsive design
- 🚧 Tournament management system

## API Documentation

The API documentation is available in:
- Detailed backend README: /backend/README.md

## Troubleshooting Common Issues

**Database Connection Problems**
- Verify MySQL service is running
- Check database credentials in `.env`
- Ensure database user has correct permissions
- Verify database exists and is accessible

**Authentication Issues**
- Confirm Google OAuth credentials are correct
- Check JWT secret is properly set
- Verify redirect URIs are configured correctly
- Ensure CORS settings match your development environment

**Development Environment**
- Verify Python and Node.js versions
- Check all dependencies are installed
- Ensure virtual environment is activated
- Verify port availability for both servers

## Contributing

While this is primarily a learning project, developers interested in the codebase can:
1. Fork the repository
2. Create a feature branch
3. Study the implementation
4. Use it as a reference for similar projects

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note:** This project is under active development. Documentation and features are continuously updated. For the most current information, please check the commit history and issue tracker.