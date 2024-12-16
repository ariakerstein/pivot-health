# Pivot Health - Digital Healthcare Platform

A cutting-edge digital healthcare platform revolutionizing medical record management through intelligent technology and secure, user-centric design.

## Tech Stack

- **Frontend:** 
  - Tailwind CSS
  - Landwind UI Framework
  - Responsive Design with Mobile-First Approach

- **Backend:**
  - Python with Flask
  - Gunicorn Web Server
  - PostgreSQL Database

- **Security:**
  - Advanced Authentication Protocols
  - HIPAA-Compliant Security Measures

## Key Features

- Professional Health Screening Services
- Personalized Health Tracking
- HIPAA-Compliant Secure Authentication
- Responsive, Accessibility-Focused Design
- Mobile-Optimized Interface

## Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **System Requirements**
   - Python 3.11+
   - Node.js and npm
   - PostgreSQL database

3. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Node.js Dependencies**
   ```bash
   npm install
   ```

5. **Environment Setup**
   Create a `.env` file in the root directory with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   SECRET_KEY=your_secret_key
   ```

6. **Database Initialization**
   ```bash
   python migrations.py init_db
   ```

7. **Start Development Servers**

   Start Tailwind CSS build process:
   ```bash
   npx tailwindcss -i ./static/css/src/main.css -o ./static/css/main.css --watch
   ```

   In a separate terminal, start Flask development server:
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:8080`

## Production Deployment

### Namecheap DNS Configuration

1. **DNS Settings**
   - Configure A records to point to your server IP
   - Add CNAME records for www subdomain
   - Configure SSL certificates

2. **Server Configuration**
   - Set environment variables:
     ```bash
     PRODUCTION=true
     PORT=8080
     DATABASE_URL=your_production_db_url
     SECRET_KEY=your_production_secret
     ```

3. **Start Production Server**
   ```bash
   gunicorn app:app --workers 4 --bind 0.0.0.0:8080
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the ISC License - see the LICENSE file for details.
