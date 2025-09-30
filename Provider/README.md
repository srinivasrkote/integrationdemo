# Provider Django Project

A Django web application project named "provider".

## Setup

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```powershell
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```powershell
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```powershell
   python manage.py runserver
   ```

The application will be available at http://127.0.0.1:8000/

## Project Structure

- `provider/` - Main Django project directory
  - `settings.py` - Django settings
  - `urls.py` - URL routing
  - `wsgi.py` - WSGI configuration
  - `asgi.py` - ASGI configuration
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies

## Development

- Use `python manage.py startapp <app_name>` to create new Django apps
- Run `python manage.py makemigrations` and `python manage.py migrate` after model changes
- Access the admin interface at http://127.0.0.1:8000/admin/