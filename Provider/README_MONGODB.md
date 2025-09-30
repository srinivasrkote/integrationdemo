# 🚀 Provider Application - MongoDB Atlas Migration Guide

This guide will help you migrate your Provider Django application from SQLite to MongoDB Atlas. Your application now supports both SQLite (for Django admin) and MongoDB Atlas (for your main application data).

## 📋 Prerequisites

1. **MongoDB Atlas Account**: [Create a free account](https://cloud.mongodb.com/)
2. **Python 3.8+**: Ensure Python is installed
3. **Virtual Environment**: Recommended for isolation

## 🏗 Architecture Overview

Your application now uses a **hybrid approach**:
- **SQLite**: For Django admin, user authentication, and sessions
- **MongoDB Atlas**: For your main application data (claims, users, documents)

This approach gives you:
- ✅ Full Django admin functionality
- ✅ Scalable MongoDB for your business data
- ✅ Easy migration path
- ✅ Best of both worlds

## 🎯 Quick Setup (5 Minutes)

### Step 1: MongoDB Atlas Setup

1. **Create Cluster**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Create a new project → "Build a Database" → Choose "M0 Sandbox" (Free)
   - Select your preferred cloud provider and region

2. **Configure Access**
   - **Database Access**: Add a new user with read/write permissions
   - **Network Access**: Add your IP address (or 0.0.0.0/0 for testing)

3. **Get Connection Details**
   - Click "Connect" → "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`)

### Step 2: Configure Your Application

1. **Update .env file** (create if it doesn't exist):
   ```env
   # MongoDB Atlas Configuration
   MONGO_DB_NAME=provider_database
   MONGO_HOST=cluster0.xxxxx.mongodb.net
   MONGO_USER=your-username
   MONGO_PASSWORD=your-password
   
   # Django Configuration
   SECRET_KEY=django-insecure-!4i!mh9^-24s(6z@uhu+xy%82k6o2tw223@*y-$)2^m=^$cx3d
   DEBUG=True
   
   # CORS Origins
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
   ```

   **Replace these values:**
   - `cluster0.xxxxx.mongodb.net` → Your cluster hostname
   - `your-username` → Your database username
   - `your-password` → Your database password

### Step 3: Run Setup

**Option A: Automated Setup (Windows)**
```bash
setup_mongodb.bat
```

**Option B: Manual Setup**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py create_mongo_sample_data
python manage.py runserver
```

## 🔌 API Endpoints

Your application now has **dual API endpoints**:

### MongoDB Endpoints (Recommended for new features)
```
POST   /api/mongo/auth/                    # MongoDB-based authentication
GET    /api/mongo/claims/                  # List claims from MongoDB
POST   /api/mongo/claims/                  # Create claim in MongoDB
GET    /api/mongo/claims/<id>/             # Get specific claim
PUT    /api/mongo/claims/<id>/             # Update claim
DELETE /api/mongo/claims/<id>/             # Delete claim
GET    /api/mongo/users/                   # List users from MongoDB
GET    /api/mongo/dashboard/stats/         # Dashboard statistics
```

### Legacy Django ORM Endpoints (For compatibility)
```
GET    /api/claims/                        # Original Django endpoints
POST   /api/claims/create/                 # Still work with SQLite
GET    /api/claims/<id>/                   # For gradual migration
```

## 🎮 Testing Your Setup

### 1. Test MongoDB Connection
```python
python -c "
from claims.mongo_models import User, Claim
print(f'Users in MongoDB: {User.objects.count()}')
print(f'Claims in MongoDB: {Claim.objects.count()}')
print('✅ MongoDB is working!')
"
```

### 2. Test API Endpoints
```bash
# Test MongoDB claims endpoint
curl http://localhost:8000/api/mongo/claims/

# Test MongoDB dashboard stats
curl http://localhost:8000/api/mongo/dashboard/stats/
```

### 3. Test Authentication
```bash
curl -X POST http://localhost:8000/api/mongo/auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "provider1", "password": "password123"}'
```

## 🔄 Migration Strategy

You can migrate gradually:

1. **Phase 1**: Keep existing frontend using old endpoints
2. **Phase 2**: Update frontend to use new MongoDB endpoints
3. **Phase 3**: Migrate existing SQLite data to MongoDB (optional)

## 🛠 Frontend Integration

Update your frontend API calls:

### Before (SQLite)
```javascript
const response = await fetch('/api/claims/');
```

### After (MongoDB)
```javascript
const response = await fetch('/api/mongo/claims/');
```

The response format is identical, so minimal frontend changes are needed!

## 📊 Sample Data

The setup creates sample data automatically:

- **Users**: 
  - `provider1` (Dr. John Smith) - Provider
  - `patient1` (Jane Doe) - Patient  
  - `patient2` (Michael Johnson) - Patient
  - `payor1` (Insurance Manager) - Payor

- **Claims**: 5 sample claims with different statuses
- **Password**: `password123` for all users (change in production!)

## 🔐 Security Notes

⚠️ **Important for Production:**

1. **Password Hashing**: Current implementation uses plain text passwords for demo purposes. Implement proper password hashing:
   ```python
   from django.contrib.auth.hashers import make_password, check_password
   user.password = make_password('plain_password')
   ```

2. **Environment Variables**: Never commit `.env` files to git
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Network Security**: Restrict MongoDB Atlas network access to specific IPs

4. **Authentication**: Implement JWT or session-based authentication

## 🚨 Troubleshooting

### Connection Issues
```
❌ MongoDB connection failed: DNS query name does not exist
```
**Solution**: Check your `MONGO_HOST` in `.env` file

### Authentication Issues
```
❌ Authentication failed
```
**Solution**: Verify `MONGO_USER` and `MONGO_PASSWORD` in `.env`

### Import Errors
```
❌ Import "mongoengine" could not be resolved
```
**Solution**: Run `pip install -r requirements.txt`

## 📈 Performance Tips

1. **Indexing**: MongoDB indexes are automatically created for common queries
2. **Denormalization**: User data is stored with claims for faster queries
3. **Connection Pooling**: MongoEngine handles connection pooling automatically

## 🎉 Success!

Your application is now running with MongoDB Atlas! 

- **Django Admin**: Still available at `/admin/` (uses SQLite)
- **API**: New MongoDB endpoints at `/api/mongo/`
- **Frontend**: Update API calls to use new endpoints
- **Scalability**: Ready for production with MongoDB Atlas

## 📞 Need Help?

1. Check the console logs for detailed error messages
2. Verify your MongoDB Atlas cluster is running
3. Test connection with the provided Python snippets
4. Ensure all environment variables are set correctly

Your Provider application is now cloud-ready with MongoDB Atlas! 🚀