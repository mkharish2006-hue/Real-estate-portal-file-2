# MVC Architecture Diagram for Real Estate Portal

## Overview
The architecture follows the Model-View-Controller (MVC) pattern, separating concerns for maintainability and scalability. This is implemented using Flask (Python) and deployed on Azure.

- **Model**: Handles data and business logic (SQLAlchemy models).
- **View**: Presents data to users (Jinja2 templates).
- **Controller**: Manages user input and application flow (Flask routes).

Based on Azure Architecture Center template: "Web Application Architecture" adapted for MVC with Azure services.

## MVC Components

### Model Layer
- **User Model**: Manages user data (registration, authentication).
- **Property Model**: Handles property listings.
- **Review Model**: Stores buyer reviews on sellers.
- **Database**: Azure SQL Database for persistence.

### View Layer
- **HTML Templates**: login.html, register.html, view_properties.html, add_property.html, property_detail.html.
- **Static Files**: CSS for styling (style.css).
- **Rendering**: Jinja2 for dynamic content.

### Controller Layer
- **Flask Routes**: Handle requests (e.g., /register, /login, /properties).
- **Business Logic**: User authentication, property CRUD, review submission.
- **Middleware**: Flask-Login for sessions, Werkzeug for security.

## Text-Based MVC Diagram (ASCII Art)

```
+-------------------+       +-------------------+       +-------------------+
|     User/Browser  | <-->  |   Controller      | <-->  |      Model        |
|                   |       | (Flask Routes)    |       | (SQLAlchemy)     |
| - Login Form      |       | - /register       |       | - User Table      |
| - Property List   |       | - /login          |       | - Property Table  |
| - Add Property    |       | - /properties     |       | - Review Table    |
| - Review Form     |       | - /add-property   |       |                   |
+-------------------+       | - /review         |       +-------------------+
                            |                   |       | Azure SQL DB      |
                            +-------------------+       +-------------------+
                                     |                           ^
                                     v                           |
                            +-------------------+       +-------------------+
                            |      View          |       |   Database Layer  |
                            | (Jinja2 Templates) |       | (ORM)             |
                            | - login.html       |       | - CRUD Operations |
                            | - view_properties.html|   | - Relationships    |
                            | - property_detail.html|   +-------------------+
                            +-------------------+
```

## Azure Integration (Architecture Center Template)
Using Azure Architecture Center's "Web Apps" template, adapted for MVC:

- **Client Layer**: Browser (HTML/CSS/JS).
- **Web Layer**: Azure App Service (Flask app).
- **Application Layer**: Controller logic.
- **Data Layer**: Azure SQL Database.
- **Supporting Services**:
  - Azure Active Directory: For authentication.
  - Azure Monitor: For logging and diagnostics.
  - Azure Key Vault: For secrets (e.g., DB connection strings).

### Deployment Flow:
1. User requests page (e.g., /properties).
2. Controller (Flask route) processes request.
3. Model queries database via SQLAlchemy.
4. Data returned to Controller.
5. Controller renders View (template) with data.
6. View sent back to User.

### Benefits of MVC in This Project:
- **Separation of Concerns**: Models handle data, Views handle UI, Controllers handle logic.
- **Scalability**: Easy to add new features (e.g., more routes/models).
- **Maintainability**: Changes to UI don't affect business logic.
- **Testability**: Each layer can be tested independently.

This architecture ensures the real estate portal is robust, secure, and aligned with Azure best practices.

## Next Steps
- **Sequence Diagrams**: For specific interactions.
- **CI/CD Pipeline**: Using Azure DevOps.
- **Deployment**: To Azure App Service.

Visualize using Azure Architecture Center or Draw.io.