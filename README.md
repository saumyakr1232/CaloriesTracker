# Calories Tracker

Calories Tracker is a FastAPI-based application designed to analyze and log food nutrition information using AI. It provides endpoints for analyzing food descriptions, tracking food images, and retrieving food logs.

## Features

- 🔍 AI-powered food analysis from text descriptions
- 📸 Image recognition for food analysis
- 📊 Detailed nutritional breakdown (calories, macros, micros)
- 📝 Food logging and tracking
- 🗄️ Database storage for historical data
- 🚀 RESTful API endpoints
- 📚 OpenAPI/Swagger documentation

## Tech Stack

- Python 3.7+
- FastAPI (ASGI Framework)
- SQLAlchemy (ORM)
- OpenAI GPT-4 (AI Analysis)
- PostgreSQL (Database)
- Uvicorn (ASGI Server)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/CaloriesTracker.git
   cd CaloriesTracker
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Set up environment variables:**

   ```bash cp .env.example .env

   ```

   - Edit .env with your configuration:
     - DATABASE_URL
     - OPENAI_API_KEY

6. **Initialize the database:**
   ```bash
   python init_db.py
   ```
7. **Run the application:**

   ```bash
   uvicorn main:app --reload
   ```

   or

   ```bash
   python main.py
   ```

   The server will start at http://localhost:8000

8. **Access the API documentation:**
   Open your web browser and navigate to . **Access the API documentation:**
   Open your web browser and navigate to URL_ADDRESS:8000/docs to view the API documentation and interact with the endpoints.

## API Endpoints

- POST /api/analyze - Analyze food from text description
- POST /api/track/image - Analyze food from image
- GET /api/logs - Retrieve food logs
- GET /api/logs/{log_id} - Get specific food log

## Development

1. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:

   ```bash
   pytest
   ```

3. Code formatting:

   ```bash
   black .
   ```

## Contributing

1. Fork the repository
2. Create your feature branch ( git checkout -b feature/AmazingFeature )
3. Commit your changes ( git commit -m 'Add some AmazingFeature' )
4. Push to the branch ( git push origin feature/AmazingFeature )
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - @saumyakr1232

Project Link: https://github.com/yourusername/CaloriesTracker

## TODO

### Security Enhancements
- [ ] Implement JWT Authentication
  - User registration and login endpoints
  - Token refresh mechanism
  - Password hashing and validation
- [ ] Add Method-level Security
  - Role-based access control (RBAC)
  - Endpoint-specific permissions
  - API key authentication for external services
- [ ] Rate Limiting
  - Implement request rate limiting per user/IP
  - Add retry mechanisms with exponential backoff
  - DDoS protection measures

### Performance Optimizations
- [ ] Implement Caching
  - Redis cache for frequently accessed data
  - Cache invalidation strategy
  - Response caching for static content
- [ ] Database Optimization
  - Index optimization
  - Query performance tuning
  - Connection pooling

### Feature Enhancements
- [ ] Data Collection Pipeline
  - User feedback collection system
  - Training data aggregation for AI model fine-tuning
  - Data validation and cleaning processes
- [ ] Advanced Analytics
  - User nutrition trends analysis
  - Meal recommendation system
  - Personalized dietary insights
- [ ] API Enhancements
  - Bulk operations support
  - Pagination for large datasets
  - Advanced filtering and search capabilities

### Infrastructure
- [ ] Monitoring and Logging
  - Implement comprehensive logging system
  - Performance monitoring
  - Error tracking and alerting
- [ ] CI/CD Pipeline
  - Automated testing
  - Deployment automation
  - Environment management
- [ ] Documentation
  - API versioning documentation
  - Integration guides
  - Contribution guidelines

### Compliance
- [ ] GDPR Compliance
  - Data privacy controls
  - User data export/deletion
  - Consent management
- [ ] Security Auditing
  - Regular security assessments
  - Vulnerability scanning
  - Compliance reporting
