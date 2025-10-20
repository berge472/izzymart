# Changing the Root Password

This guide explains how to change the root admin password from within the running API container.

## From Inside the Container

### Method 1: Using the Python Script (Recommended)

1. **Access the container shell:**
   ```bash
   # Get the pod name
   kubectl get pods -n izzymart

   # SSH into the API pod
   kubectl exec -it izzymart-api-xxxxx-xxxxx -n izzymart -- /bin/bash
   ```

2. **Run the password change script:**
   ```bash
   cd /app
   python3 change_root_password.py
   ```

3. **Follow the prompts:**
   - Enter your new password (minimum 8 characters)
   - Confirm the password
   - The script will update the database

### Method 2: Using the Shell Script

Alternatively, you can use the wrapper script:

```bash
cd /app
./change-password.sh
```

## From Outside the Container

You can also run the script directly from kubectl:

```bash
kubectl exec -it izzymart-api-xxxxx-xxxxx -n izzymart -- python3 /app/change_root_password.py
```

## Script Features

✅ **Password validation** - Ensures password is at least 8 characters
✅ **Confirmation prompt** - Asks you to confirm the password
✅ **Bcrypt hashing** - Securely hashes the password
✅ **Database update** - Updates the root user in MongoDB
✅ **Error handling** - Clear error messages if something goes wrong

## Security Notes

- The password is hashed using bcrypt before being stored
- Bcrypt has a 72-byte limit; passwords longer than this will be truncated
- The password is not visible when you type it (for security)
- The script requires access to the MongoDB database

## Troubleshooting

### "Root user not found"
The root user doesn't exist in the database. The API should create it automatically on first startup.

### "Error connecting to database"
Check that:
- MongoDB is running
- `MONGO_HOST` environment variable is correct
- Network connectivity to MongoDB

### "Failed to update password"
Check the error message for details. Common issues:
- Database connection problems
- Insufficient permissions
- Invalid characters in password

## Example Session

```bash
$ python3 change_root_password.py
============================================================
IzzyMart - Change Root Password
============================================================

📡 Connecting to MongoDB at izzymart-mongodb:27017...
✅ Connected to database

👤 Found root user (ID: 000000000000000000000000)

Please enter the new password for the root user.
Note: Password will not be visible as you type.

New password: ********
Confirm password: ********

🔄 Updating password...
✅ Root password updated successfully!

============================================================
🎉 Password changed successfully!
============================================================

You can now log in to the admin panel with your new password.
Username: root
Password: (the password you just set)
```
