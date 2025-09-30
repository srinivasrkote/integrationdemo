# MongoDB Atlas Setup Guide

This guide will help you migrate your Provider Django application from SQLite to MongoDB Atlas.

## Prerequisites

1. **MongoDB Atlas Account**: Create a free account at [MongoDB Atlas](https://cloud.mongodb.com/)
2. **Python Environment**: Ensure you have Python 3.8+ installed
3. **Virtual Environment**: Recommended to use a virtual environment

## Step 1: MongoDB Atlas Cluster Setup

### Create a Cluster
1. Log in to MongoDB Atlas
2. Create a new project (if you don't have one)
3. Click "Build a Database" → "Shared" (free tier)
4. Choose your cloud provider and region
5. Create your cluster (this may take 2-3 minutes)

### Configure Database Access
1. Go to "Database Access" in the left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Set username and password (remember these for your .env file)
5. Set database user privileges to "Read and write to any database"
6. Click "Add User"

### Configure Network Access
1. Go to "Network Access" in the left sidebar
2. Click "Add IP Address"
3. Choose "Allow Access from Anywhere" (for development) or add your specific IP
4. Click "Confirm"

### Get Connection String
1. Go to "Databases" in the left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string (it looks like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/<dbname>?retryWrites=true&w=majority`)

## Step 2: Configure Your Django Application

### Update .env File
Update your `.env` file with your MongoDB Atlas credentials:

```env
# MongoDB Atlas Configuration
MONGO_DB_NAME=provider_database
MONGO_HOST=your-cluster-name.xxxxx.mongodb.net
MONGO_USER=your-username
MONGO_PASSWORD=your-password

# Django Configuration
SECRET_KEY=your-secret-key
DEBUG=True

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
```

**Important**: Replace the placeholders with your actual MongoDB Atlas credentials:
- `your-cluster-name.xxxxx.mongodb.net`: Your cluster hostname from the connection string
- `your-username`: The database username you created
- `your-password`: The database password you created
- `provider_database`: Your preferred database name

## Step 3: Install Dependencies and Setup

### Option 1: Automated Setup (Recommended)
Run the automated setup script:

```bash
python setup_mongodb.py
```

This script will:
- Install all required packages
- Verify your MongoDB Atlas connection
- Run database migrations
- Create sample data

### Option 2: Manual Setup

1. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test MongoDB Connection**:
   ```python
   python -c "
   import pymongo
   from decouple import config
   
   mongo_user = config('MONGO_USER')
   mongo_password = config('MONGO_PASSWORD')
   mongo_host = config('MONGO_HOST')
   
   client = pymongo.MongoClient(f'mongodb+srv://{mongo_user}:{mongo_password}@{mongo_host}/test?retryWrites=true&w=majority')
   print('Connection successful:', client.server_info())
   client.close()
   "
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate --run-syncdb
   ```

4. **Create Sample Data**:
   ```bash
   python manage.py create_sample_data
   ```

## Step 4: Run the Application

Start the Django development server:

```bash
python manage.py runserver
```

Your application should now be running with MongoDB Atlas as the database!

## Troubleshooting

### Common Issues

1. **Connection Timeout**:
   - Check your network access settings in MongoDB Atlas
   - Ensure your IP address is whitelisted
   - Verify your internet connection

2. **Authentication Failed**:
   - Double-check your username and password in the .env file
   - Ensure the database user has proper permissions

3. **Import Errors**:
   - Make sure all packages are installed: `pip install -r requirements.txt`
   - Check if you're in the correct virtual environment

4. **Migration Issues**:
   - Try running migrations with `--fake-initial` flag if needed
   - Clear migration files if necessary (backup first!)

### Verification Steps

1. **Check Database Connection**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.db import connection
   connection.ensure_connection()
   print("Database connected successfully!")
   ```

2. **Verify Data Creation**:
   ```bash
   python manage.py shell
   ```
   ```python
   from accounts.models import User
   from claims.models import Claim
   print(f"Users: {User.objects.count()}")
   print(f"Claims: {Claim.objects.count()}")
   ```

## MongoDB Atlas Features

### Monitoring
- Use MongoDB Atlas's built-in monitoring tools
- View real-time metrics and performance insights
- Set up alerts for important events

### Backup
- Automatic backups are enabled by default
- Configure backup policies in the Atlas interface

### Security
- Enable additional security features like IP whitelisting
- Use MongoDB Atlas encryption features
- Regularly rotate database passwords

## Next Steps

1. **Frontend Integration**: Your existing frontend should work without changes
2. **API Testing**: Test all API endpoints to ensure proper functionality
3. **Production Setup**: Configure environment-specific settings for production
4. **Performance Optimization**: Consider MongoDB indexing for better performance

## Support

If you encounter any issues:
1. Check the Django logs for detailed error messages
2. Verify your MongoDB Atlas cluster status
3. Consult MongoDB Atlas documentation
4. Check Django-MongoDB integration guides

Your Provider application is now successfully using MongoDB Atlas! 🎉