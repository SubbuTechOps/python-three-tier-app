import mysql.connector
import bcrypt
import os
import time

# Get database configuration from environment variables
db_config = {
    'host': os.getenv('DB_HOST', 'db'),
    'user': os.getenv('DB_USER', 'subbu'),
    'password': os.getenv('DB_PASSWORD', 'admin@1234'),
    'database': os.getenv('DB_NAME', 'ecommerce'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def wait_for_db():
    """Wait for database to be ready"""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = mysql.connector.connect(**db_config)
            conn.close()
            print("Database is ready!")
            return True
        except mysql.connector.Error as err:
            attempt += 1
            print(f"Database not ready, waiting... (Attempt {attempt}/{max_attempts})")
            time.sleep(2)
    
    raise Exception("Could not connect to database after maximum attempts")

def update_password_hashes():
    """Update plain text passwords with bcrypt hashes"""
    try:
        # First wait for database to be ready
        wait_for_db()
        
        # Connect to the database
        print("Connecting to database...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get all users
        print("Fetching users...")
        cursor.execute("SELECT id, username, password FROM users")
        users = cursor.fetchall()
        
        # Update each user's password with a hash
        updated_count = 0
        skipped_count = 0
        
        for user in users:
            # Skip already hashed passwords (those starting with $2b$)
            if user['password'].startswith('$2b$'):
                print(f"Skipping already hashed password for user: {user['username']}")
                skipped_count += 1
                continue
                
            try:
                # Hash the plain text password
                hashed = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
                
                # Update the user's password in the database
                update_query = "UPDATE users SET password = %s WHERE id = %s"
                cursor.execute(update_query, (hashed.decode('utf-8'), user['id']))
                print(f"Updated password for user: {user['username']}")
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating password for user {user['username']}: {str(e)}")
        
        # Commit the changes
        conn.commit()
        print("\nPassword update summary:")
        print(f"Total users processed: {len(users)}")
        print(f"Passwords updated: {updated_count}")
        print(f"Already hashed (skipped): {skipped_count}")
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    print("Starting password update process...")
    update_password_hashes()
    print("Password update process completed!")
