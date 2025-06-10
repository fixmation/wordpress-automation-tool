
Built by https://www.blackbox.ai

---

# WordPress Automation Tool

## Project Overview
The WordPress Automation Tool is a web application designed for automating various tasks related to WordPress management using Flask. This tool simplifies processes like SQLite database migrations and WordPress automation tasks. The application features a login system, a dashboard for managing WordPress sites, and a cross-platform website builder.

## Installation
To install and run the WordPress Automation Tool, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your_username/wordpress-automation-tool.git
   cd wordpress-automation-tool
   ```

2. **Install dependencies:**
   You need to have Node.js and Python installed. Next, you can use npm to install the JavaScript dependencies:
   ```bash
   npm install
   ```

3. **Set up Python environment:**
   Install Flask and Flask-Login if not already installed:
   ```bash
   pip install Flask Flask-Login
   ```

4. **Set environment variables:**
   Ensure to set the `SECRET_KEY` variable for Flask. You can do this in your terminal:
   ```bash
   export SECRET_KEY='your_secret_key'
   ```

5. **Run the application:**
   Run the Flask app:
   ```bash
   python app.py
   ```

## Usage
1. Open your web browser and navigate to `http://localhost:8000`.
2. The app will redirect you to the login page. Use the credentials:
   - Username: `admin`
   - Password: `admin`
3. After logging in, you can create and manage WordPress sites via the dashboard.

## Features
- SQLite database migration management.
- Basic WordPress automation functionality.
- User authentication using Flask-Login.
- Create websites for multiple platforms.
- Responsive dashboard.

## Dependencies
The project has the following dependencies listed in `package.json`:

- `@types/node`: TypeScript definitions for Node.js
- `axios`: Promise-based HTTP client for the browser and Node.js
- `react`: A JavaScript library for building user interfaces
- `react-dom`: Serves as the entry point for DOM-related rendering
- `react-router-dom`: DOM bindings for React Router

In addition, the project uses the following development dependencies:

- `@types/react`: TypeScript definitions for React
- `@types/react-dom`: TypeScript definitions for React DOM
- `@typescript-eslint/eslint-plugin`: TypeScript-specific linting rules for ESLint
- `@typescript-eslint/parser`: ESLint parser for TypeScript
- `@vitejs/plugin-react`: Vite plugin for React
- `eslint`: Linting utility for JavaScript and JSX
- `eslint-plugin-react-hooks`: Linting rules for React Hooks
- `eslint-plugin-react-refresh`: Plugin for enabling react-refresh in development
- `typescript`: A superset of JavaScript that adds static types

## Project Structure
The project is organized as follows:

```
wordpress-automation-tool/
├── WordPressAutomationTool/
│   ├── templates/                         # HTML templates for rendering
├── migrations/                            # SQL migration files
├── app.py                                 # Main Flask application file
├── simple_app.py                          # Simple Flask app for demonstration
├── new_app.py                             # Updated Flask app with authentication
├── simple_no_auth_app.py                  # Basic Flask app without authentication
├── abilities.py                           # Functions for database and WordPress automation
├── package.json                           # Project metadata and dependencies
└── package-lock.json                      # Locked versions of dependencies
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.