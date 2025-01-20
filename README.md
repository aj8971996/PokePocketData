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
1. Install MySQL Server 8.0 and MySQL Workbench
2. Create a new connection in MySQL Workbench:
   - Connection Name: PokePocketData_Local
   - Hostname: localhost
   - Port: 3306
   - Username: ppdd_api_user (create this user for API connections)

3. Create a `.env` file in the backend directory with your database configuration:
```plaintext
DB_USER=ppdd_api_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
```

Note: Never commit the `.env` file to version control. A `.env.example` template is provided for reference.

## Installation
1. Clone the repository
```bash
git clone https://github.com/[your-username]/PokePocketData.git
cd PokePocketData
```

2. Install frontend dependencies
```bash
npm install
```

3. Install Python dependencies (Backend)
```bash
cd backend
pip install -r requirements.txt
```

4. Initialize the database
```bash
python init_db.py  # This will create the database and tables
```

5. Start the backend server
```bash
python main.py
```

6. Start the frontend development server
```bash
cd ../frontend
ng serve
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Development Status
🚧 The project is currently in the initial setup phase, with the following completed:
- Basic project structure
- Database models defined
- Database connection configuration
- Initial API user setup

## Local Development Notes
- This project is designed for local development and learning purposes
- Database connections are configured for localhost only
- Environment variables should be set up locally using the provided `.env.example` template
- API user (ppdd_api_user) is configured with local-only permissions

## Contributing
As this is a personal development project, contributions are currently not being accepted. Feel free to fork the repository for your own learning purposes.

---
**Note:** This README will be updated as the project evolves and new features are implemented.