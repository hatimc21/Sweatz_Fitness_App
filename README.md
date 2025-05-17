# Sweatz Fitness App

An all-in-one fitness application for tracking nutrition, body metrics, and workout progress with AI assistance and smartwatch integration.

## Overview

Sweatz is a comprehensive fitness platform designed to replace multiple fitness apps with a single, integrated solution. The application allows users to track their nutrition, monitor body metrics, plan workouts, and visualize their progress over time.

## Features

- **Progress Tracking**: Monitor nutrition, body metrics, and workout performance
- **AI Gym Assistant**: Receive personalized workout and nutrition guidance
- **Workout Planning**: Create and manage custom workout routines
- **Smartwatch Integration**: Track workouts in real-time with wearable devices
- **Reminder System**: Stay consistent with customizable notifications

## Technology Stack

- **Backend**: Python/Flask
- **Database**: MongoDB
- **Authentication**: JWT and session-based
- **Frontend**: Responsive HTML/CSS/JavaScript (for web), WebView for mobile
- **Charts**: Chart.js
- **API**: RESTful architecture

## Setup & Installation

### Prerequisites
- Python 3.10+
- MongoDB
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository
```bash
git clone https://github.com/hatimc21/Sweatz_Fitness_App.git
cd sweatz-app
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Create a .env file and add the following variables
MONGO_USERNAME=your_mongodb_username
MONGO_PASSWORD=your_mongodb_password
MONGO_CLUSTER=your_mongodb_cluster
MONGO_DATABASE=sweatz_dev
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

5. Run the application
```bash
python run.py
```

## Project Structure

```
sweatz-app/
│
├── app/                            # Main application package
│   ├── api/                        # API endpoints
│   ├── models/                     # Database models
│   ├── services/                   # Business logic
│   ├── static/                     # Static files (CSS, JS, images)
│   ├── templates/                  # HTML templates
│   └── utils/                      # Utility functions
│
├── mobile/                         # Mobile app wrapper
│
├── migrations/                     # Database migrations
│
├── tests/                          # Test suite
│
├── .env                            # Environment variables
├── .gitignore                      # Git ignore file
├── requirements.txt                # Python dependencies
└── run.py                          # Application entry point
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/auth/register | POST | User registration |
| /api/auth/login | POST | User login |
| /api/auth/logout | GET | User logout |
| /admin/* | GET/POST | Admin dashboard |

## Admin Dashboard

Access the admin dashboard at `/admin` to:
- View user statistics
- Manage user accounts
- Configure system settings
- Maintain exercise database

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Hatim - chifahatim1@gmail.com

