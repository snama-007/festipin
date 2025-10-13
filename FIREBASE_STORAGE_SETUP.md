# Firebase Storage Setup Guide

## Issue
The Firebase Storage bucket `festpin.appspot.com` doesn't exist yet, causing upload failures.

## Solution: Create Firebase Storage Bucket

### Option 1: Using Firebase Console (Recommended)

1. **Go to Firebase Console:**
   - Visit: https://console.firebase.google.com/
   - Select your project: **festpin**

2. **Navigate to Storage:**
   - In the left sidebar, click **"Build"** → **"Storage"**
   - Click **"Get Started"**

3. **Set Security Rules:**
   Choose **"Start in production mode"** or **"Start in test mode"**
   
   **Production Mode** (Recommended):
   ```javascript
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /{allPaths=**} {
         allow read: if true;  // Public read access
         allow write: if request.auth != null;  // Authenticated write
       }
     }
   }
   ```
   
   **Test Mode** (For Development - Less Secure):
   ```javascript
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /{allPaths=**} {
         allow read, write: if true;  // Full public access
       }
     }
   }
   ```

4. **Select Location:**
   - Choose a location close to your users (e.g., `us-central1`, `asia-south1`, etc.)
   - Click **"Done"**

5. **Verify Bucket Name:**
   - After creation, note your bucket name
   - It should be: `festpin.appspot.com` or similar
   - Update `backend/app/core/config.py` if different:
     ```python
     FIREBASE_STORAGE_BUCKET: str = "your-actual-bucket-name"
     ```

### Option 2: Using Firebase CLI

```bash
# Install Firebase CLI (if not installed)
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase Storage
cd /path/to/your/project
firebase init storage

# Follow prompts:
# - Select your project: festpin
# - Use default rules or customize
# - Deploy
firebase deploy --only storage
```

### Option 3: Using Google Cloud Console

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Select project: **festpin**

2. **Navigate to Cloud Storage:**
   - Click menu → **"Cloud Storage"** → **"Buckets"**
   - Click **"Create Bucket"**

3. **Configure Bucket:**
   - **Name**: `festpin.appspot.com`
   - **Location**: Choose your preferred region
   - **Storage class**: Standard
   - **Access control**: Fine-grained
   - Click **"Create"**

4. **Set Permissions:**
   - Go to bucket → **"Permissions"** tab
   - Add principal: `allUsers`
   - Role: **"Storage Object Viewer"** (for public read access)

## After Creating the Bucket

### Enable Firebase Storage in Your Backend

1. **Update configuration:**
   ```bash
   cd /Users/snama/s.space/Parx-Agentic-Verse/festipin/backend
   ```

2. **Edit `app/core/config.py`:**
   ```python
   USE_LOCAL_STORAGE: bool = False  # Enable Firebase Storage
   FIREBASE_STORAGE_BUCKET: str = "festpin.appspot.com"  # Your bucket name
   ```

3. **Restart backend:**
   ```bash
   # Kill existing process
   pkill -f "uvicorn"
   
   # Start with Firebase Storage
   cd backend && source venv/bin/activate
   python -m uvicorn app.main:app --reload --port 9000
   ```

## Verify Setup

Test the storage connection:
```bash
curl -X POST http://localhost:9000/api/v1/vision/upload \
  -F "file=@/path/to/test-image.jpg"
```

You should see a successful response with an image URL from Firebase Storage.

## Current Status

✅ **Local Storage**: Currently active (working)
⚠️ **Firebase Storage**: Bucket needs to be created
📝 **Action Required**: Follow steps above to create Firebase Storage bucket

## Quick Toggle

To switch between local and Firebase storage, edit `backend/app/core/config.py`:

```python
# Use Local Storage (current)
USE_LOCAL_STORAGE: bool = True

# Use Firebase Storage (after setup)
USE_LOCAL_STORAGE: bool = False
```

The backend will auto-reload with the new configuration.

