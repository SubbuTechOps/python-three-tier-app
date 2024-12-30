# ShopEasy E-commerce Application
[Previous sections remain the same...]

## 9. Project Setup and Deployment Guide

### 9.1 Prerequisites
- Git
- Docker
- Docker Compose
- Make (optional, for Makefile commands)

### 9.2 Project Setup Steps

1. **Clone the Repository**
```bash
# Clone the repository
git clone https://github.com/yourusername/shopeasy.git
cd shopeasy
```

2. **Environment Configuration**
```bash
# Copy example environment file
cp .env.example .env

# Update .env file with your configurations
DB_HOST=db
DB_USER=subbu
DB_PASSWORD=admin@1234
DB_NAME=ecommerce
SECRET_KEY=your_secure_secret_key
FLASK_DEBUG=True
PORT=5000
SESSION_FILE_DIR=/tmp/flask_sessions
```

3. **Project Structure**
```
shopeasy/
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── database/
│   └── Dockerfile.backend
├── frontend/
│   ├── index.html
│   ├── catalog.html
│   ├── cart.html
│   └── styles.css
├── docker/
│   └── docker-compose.yaml
├── .env
└── README.md
```

4. **Docker Compose Deployment**
```bash
# Build and start containers
docker compose -f docker/docker-compose.yaml up --build

# To run in detached mode
docker compose -f docker/docker-compose.yaml up --build -d

# To stop the containers
docker compose -f docker/docker-compose.yaml down

# To view logs
docker compose -f docker/docker-compose.yaml logs -f
```

5. **Database Initialization**
```bash
# Database migrations and initial data will be loaded automatically 
# from the SQL files in backend/database/ directory:
- 01_schema.sql
- 02_data.sql
```

6. **Verify Deployment**
- Access the application: http://localhost:5000
- Check container status:
```bash
docker compose -f docker/docker-compose.yaml ps
```

7. **Troubleshooting Commands**
```bash
# Check backend logs
docker compose -f docker/docker-compose.yaml logs -f backend

# Check database logs
docker compose -f docker/docker-compose.yaml logs -f db

# Restart specific service
docker compose -f docker/docker-compose.yaml restart backend

# Remove volumes and clean start
docker compose -f docker/docker-compose.yaml down -v
docker compose -f docker/docker-compose.yaml up --build
```

### 9.3 Initial Data and Testing
1. Default test account:
   - Username: subbu
   - Password: admin@1234

2. Test the deployment:
   - Visit http://localhost:5000
   - Login with test credentials
   - Browse catalog
   - Add items to cart
   - Place test order

### 9.4 Common Issues and Solutions

1. **Database Connection Issues**
```bash
# Check if database is running
docker compose -f docker/docker-compose.yaml ps db

# Check database logs
docker compose -f docker/docker-compose.yaml logs db

# Manual database connection test
docker compose -f docker/docker-compose.yaml exec db mysql -u subbu -p
```

2. **Session Issues**
```bash
# Check session directory permissions
docker compose -f docker/docker-compose.yaml exec backend ls -la /tmp/flask_sessions

# Clear sessions
docker compose -f docker/docker-compose.yaml exec backend rm -rf /tmp/flask_sessions/*
```

3. **Port Conflicts**
```bash
# Check if ports are in use
netstat -tulpn | grep 5000
netstat -tulpn | grep 3306

# Change ports in docker-compose.yaml if needed
```

### 9.5 Development Commands

1. **Access Container Shell**
```bash
# Backend container
docker compose -f docker/docker-compose.yaml exec backend bash

# Database container
docker compose -f docker/docker-compose.yaml exec db bash
```

2. **Database Management**
```bash
# Create database backup
docker compose -f docker/docker-compose.yaml exec db mysqldump -u subbu -p ecommerce > backup.sql

# Restore database
docker compose -f docker/docker-compose.yaml exec -T db mysql -u subbu -p ecommerce < backup.sql
```

3. **Code Updates**
```bash
# Apply code changes
docker compose -f docker/docker-compose.yaml restart backend

# View updated logs
docker compose -f docker/docker-compose.yaml logs -f backend
```

### 9.6 Production Deployment Notes

1. **Security Considerations**
- Update SECRET_KEY in .env
- Set FLASK_DEBUG=False
- Use proper SSL/TLS certificates
- Update database passwords
- Remove test accounts

2. **Performance Optimization**
- Configure proper database indexes
- Set up proper logging
- Configure backup strategy
- Set up monitoring

3. **Scaling Notes**
- Configure load balancer if needed
- Set up database replication
- Configure proper cache strategy
- Set up proper monitoring and alerts

[Rest of the document remains the same...]
