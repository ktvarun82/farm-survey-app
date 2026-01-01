# Farm Survey Application

A full-stack web application for managing farm surveys, built with FastAPI (backend) and vanilla JavaScript (frontend). The application allows users to create, view, update, and delete farm survey records with geographic location tracking and conflict resolution capabilities.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Frontend Usage](#frontend-usage)
- [File Descriptions](#file-descriptions)

## ✨ Features

- **CRUD Operations**: Create, Read, Update, and Delete farm surveys
- **Geographic Location Tracking**: Store latitude and longitude coordinates for each survey
- **Conflict Resolution**: Optimistic locking using `last_updated` timestamps to prevent concurrent modification conflicts
- **Synchronization Status**: Track whether surveys have been synced with external systems
- **Responsive Web Interface**: Modern, mobile-friendly frontend with intuitive UI
- **RESTful API**: Well-documented API endpoints following REST principles
- **Automatic Timestamps**: Tracks when surveys are created and last modified

## 🏗️ Architecture

The application follows a clean, layered architecture:

```
┌─────────────────┐
│   Frontend      │  (HTML/CSS/JavaScript)
│  (Browser)      │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│   FastAPI       │  (Python Web Framework)
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────┐
│ Models │  │ Schemas  │  (Data Validation)
│(SQLAlch)│  │(Pydantic)│
└────────┘  └──────────┘
    │
    ▼
┌──────────────┐
│   SQLite     │
│  Database    │
└──────────────┘
```

### Data Flow

1. **Request**: Frontend sends HTTP request to FastAPI
2. **Validation**: Pydantic schemas validate input data
3. **Processing**: FastAPI routes handle business logic
4. **Database**: SQLAlchemy ORM interacts with SQLite database
5. **Response**: Validated data returned to frontend
6. **Display**: JavaScript updates the UI

## 📁 Project Structure

```
Farm Survey/
│
├── main.py                 # FastAPI application and route handlers
├── database.py             # Database configuration and session management
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic validation schemas
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies (frontend)
├── tsconfig.json           # TypeScript configuration
├── farm_survey.db          # SQLite database file (auto-generated)
│
├── src/                    # TypeScript source files
│   ├── app.ts             # Main application logic (TypeScript)
│   └── types.ts           # Type definitions
│
└── static/                 # Frontend files
    ├── index.html          # Main HTML page
    ├── css/
    │   └── style.css       # Stylesheet
    └── js/
        └── app.js          # Compiled JavaScript (generated from TypeScript)
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.104.1): Modern, fast web framework for building APIs
- **SQLAlchemy** (2.0.23): SQL toolkit and ORM
- **Pydantic** (2.5.0): Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI
- **SQLite**: Lightweight database (file-based)

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with modern features (Grid, Flexbox, Gradients)
- **TypeScript**: Type-safe JavaScript with modern features
- **esbuild**: Fast bundler for TypeScript compilation
- **Fetch API**: For HTTP requests

## 🚀 Setup and Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "D:\AI\Cursor\Farm Survey"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - FastAPI
   - Uvicorn
   - SQLAlchemy
   - Pydantic

3. **Install Node.js dependencies** (for frontend)
   ```bash
   npm install
   ```

   This will install:
   - TypeScript
   - esbuild (bundler)

4. **Build the frontend**
   ```bash
   npm run build
   ```

   This compiles TypeScript to JavaScript.

3. **Database Setup**
   - The database file (`farm_survey.db`) will be automatically created on first run
   - SQLAlchemy will create the table schema automatically

## ▶️ Running the Application

### Start the Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or using Python's `-m` flag:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Access the Application

- **Frontend**: [http://localhost:8000](http://localhost:8000)
- **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

The `--reload` flag enables auto-reloading when code changes are detected.

## 🗄️ Database Schema

### `farm_surveys` Table

| Column       | Type      | Constraints           | Description                              |
|--------------|-----------|-----------------------|------------------------------------------|
| survey_id    | Integer   | Primary Key, Index    | Unique identifier for the survey         |
| farmer_name  | String    | Not Null, Index       | Name of the farmer                       |
| crop_type    | String    | Not Null              | Type of crop (e.g., "Wheat", "Corn")     |
| latitude     | Float     | Not Null              | Latitude coordinate (-90 to 90)          |
| longitude    | Float     | Not Null              | Longitude coordinate (-180 to 180)       |
| sync_status  | Boolean   | Not Null, Default: False | Whether survey is synced with external system |
| last_updated | DateTime  | Not Null, Auto-update | Timestamp of last modification (for conflict resolution) |

### Database Relationships

- No foreign keys (single table design)
- Indexes on `survey_id` (primary key) and `farmer_name` for faster queries

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. **GET /** - Serve Frontend
- **Description**: Returns the HTML frontend page
- **Response**: HTML file (`static/index.html`)

#### 2. **POST /surveys/** - Create Survey
- **Description**: Create a new farm survey
- **Request Body**:
  ```json
  {
    "farmer_name": "John Doe",
    "crop_type": "Wheat",
    "geo_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "sync_status": false
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "survey_id": 1,
    "farmer_name": "John Doe",
    "crop_type": "Wheat",
    "geo_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "sync_status": false,
    "last_updated": "2024-01-15T10:30:00"
  }
  ```

#### 3. **GET /surveys/** - List All Surveys
- **Description**: Get all farm surveys (paginated)
- **Query Parameters**:
  - `skip` (optional): Number of records to skip (default: 0)
  - `limit` (optional): Maximum number of records to return (default: 100)
- **Response**: `200 OK`
  ```json
  [
    {
      "survey_id": 1,
      "farmer_name": "John Doe",
      ...
    }
  ]
  ```

#### 4. **GET /surveys/{survey_id}** - Get Survey by ID
- **Description**: Retrieve a specific survey by its ID
- **Path Parameters**:
  - `survey_id` (integer): The survey ID
- **Response**: `200 OK` (survey object) or `404 Not Found`

#### 5. **PUT /surveys/{survey_id}** - Update Survey
- **Description**: Update an existing survey with conflict resolution
- **Path Parameters**:
  - `survey_id` (integer): The survey ID
- **Query Parameters**:
  - `last_updated` (optional, datetime): Timestamp for conflict resolution
- **Request Body** (all fields optional):
  ```json
  {
    "farmer_name": "Jane Doe",
    "crop_type": "Corn",
    "geo_location": {
      "latitude": 41.8781,
      "longitude": -87.6298
    },
    "sync_status": true
  }
  ```
- **Response**: `200 OK` (updated survey) or `409 Conflict` (if `last_updated` doesn't match)

#### 6. **DELETE /surveys/{survey_id}** - Delete Survey
- **Description**: Delete a survey by ID
- **Path Parameters**:
  - `survey_id` (integer): The survey ID
- **Response**: `204 No Content` or `404 Not Found`

### Conflict Resolution

The update endpoint implements optimistic locking:

1. When fetching a survey, note the `last_updated` timestamp
2. When updating, include the `last_updated` timestamp as a query parameter
3. The server compares the provided timestamp with the current database timestamp
4. If they differ by more than 1 second, a `409 Conflict` error is returned
5. This prevents overwriting changes made by other users/clients

**Example**:
```http
PUT /surveys/1?last_updated=2024-01-15T10:30:00
```

## 🖥️ Frontend Usage

### Main Interface

The frontend provides a two-column layout:

1. **Left Column - Survey Form**
   - Create new surveys
   - Edit existing surveys (when in edit mode)
   - Form fields:
     - Farmer Name (required)
     - Crop Type (required)
     - Latitude (required, -90 to 90)
     - Longitude (required, -180 to 180)
     - Sync Status (checkbox)

2. **Right Column - Surveys List**
   - Display all surveys in card format
   - Each card shows:
     - Survey ID
     - Farmer Name
     - Crop Type
     - Geographic Coordinates
     - Sync Status (with color-coded badge)
     - Last Updated timestamp
     - Edit and Delete buttons

### User Interactions

- **Create Survey**: Fill form and click "Create Survey"
- **Edit Survey**: Click "Edit" button on any survey card
  - Form populates with survey data
  - Click "Update Survey" to save changes
  - Click "Cancel" to exit edit mode
- **Delete Survey**: Click "Delete" button and confirm
- **Refresh**: Click "Refresh" button to reload all surveys

### Error Handling

- Success messages (green) appear at the top for successful operations
- Error messages (red) appear for failed operations
- Conflict errors show when update conflicts are detected
- All messages auto-dismiss after a few seconds

## 📄 File Descriptions

### `main.py`
The main FastAPI application file containing:
- FastAPI app instance
- Static file mounting
- Route handlers for all API endpoints
- Helper function to convert database models to Pydantic schemas
- Database session dependency injection

**Key Functions**:
- `read_root()`: Serves the frontend HTML file
- `create_survey()`: Creates a new survey
- `get_surveys()`: Lists all surveys
- `get_survey()`: Gets a single survey
- `update_survey()`: Updates a survey with conflict resolution
- `delete_survey()`: Deletes a survey
- `_db_to_schema()`: Converts SQLAlchemy model to Pydantic schema

### `database.py`
Database configuration and session management:
- SQLite database URL configuration
- SQLAlchemy engine setup
- Session factory (SessionLocal)
- Base class for ORM models
- `get_db()` dependency function for FastAPI dependency injection

**Key Components**:
- `SQLALCHEMY_DATABASE_URL`: Database connection string
- `engine`: SQLAlchemy engine instance
- `SessionLocal`: Session factory
- `Base`: Declarative base for models
- `get_db()`: Dependency that provides database sessions

### `models.py`
SQLAlchemy ORM models defining the database schema:
- `FarmSurvey`: Main model class representing the `farm_surveys` table

**Model Fields**:
- All fields match the database schema (see Database Schema section)
- Uses SQLAlchemy column types
- Defines table name and constraints

### `schemas.py`
Pydantic models for request/response validation:
- `GeoLocation`: Nested model for latitude/longitude with validation
- `FarmSurveyBase`: Base schema with common fields
- `FarmSurveyCreate`: Schema for creating surveys (inherits from Base)
- `FarmSurveyUpdate`: Schema for updates (all fields optional)
- `FarmSurvey`: Response schema (includes `survey_id` and `last_updated`)

**Validation Features**:
- Latitude/longitude range validation
- String length validation
- Type checking
- Example schemas for API documentation

### `static/index.html`
Frontend HTML structure:
- Main page layout
- Survey form
- Surveys list container
- Links to CSS and JavaScript files

### `static/css/style.css`
Styling for the frontend:
- Modern gradient background
- Responsive grid layout
- Card-based survey display
- Form styling
- Button styles and hover effects
- Color-coded sync status badges
- Animations and transitions

### `src/app.ts`
Main TypeScript application file (source code):
- Type-safe API communication using Fetch API
- DOM manipulation with type assertions
- Form handling with typed data structures
- Error and success message display
- Survey card rendering
- Edit/Delete functionality

**Key Functions**:
- `loadSurveys()`: Fetches and displays all surveys
- `createSurveyCard()`: Creates HTML for a survey card
- `handleFormSubmit()`: Handles form submission (create/update)
- `editSurvey()`: Loads survey data into form for editing
- `deleteSurvey()`: Deletes a survey after confirmation
- `resetForm()`: Clears form and exits edit mode
- `showError()` / `showSuccess()`: Display user feedback messages

### `src/types.ts`
TypeScript type definitions:
- Interface definitions for all data structures
- Type-safe API request/response types
- Geographic location types
- Error response types

### `static/js/app.js`
Compiled JavaScript (generated from TypeScript):
- **Note**: This file is auto-generated - edit `src/app.ts` instead
- Bundled and optimized by esbuild
- Browser-compatible JavaScript

### `requirements.txt`
Python package dependencies with version numbers:
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic

## 🔒 Security Considerations

- Input validation via Pydantic schemas
- SQL injection protection through SQLAlchemy ORM
- XSS prevention through HTML escaping in JavaScript
- Conflict resolution prevents data loss from concurrent updates

## 🚧 Future Enhancements

Potential improvements:
- User authentication and authorization
- Role-based access control
- File uploads for survey attachments
- Map visualization for geographic locations
- Advanced filtering and search
- Export functionality (CSV, JSON)
- Bulk operations
- Offline support with sync
- Email notifications
- Audit logging

## 📝 Notes

- The database file (`farm_survey.db`) is created automatically
- SQLite is used for simplicity; for production, consider PostgreSQL or MySQL
- The `last_updated` field uses UTC timezone
- Static files are served from the `/static` path
- API documentation is automatically generated by FastAPI

## 🤝 Support

For issues or questions, refer to:
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Pydantic Documentation: https://docs.pydantic.dev/

---

**Version**: 1.0.0  
**Last Updated**: 2024

