# Live Scoreboard

Real-time event management and live scoreboard platform. Organizers log in, add participants and scores, and every open screen updates instantly over WebSockets.

## Features
- JWT authentication with organizer and participant roles
- Event and participant management through a REST API
- Live leaderboard: score updates reach all viewers without a page refresh
- Role-based access: only organizers can add scores

## Tech Stack
- **Frontend:** React, Vite, Tailwind CSS, Socket.IO client
- **Backend:** Flask, Flask-SocketIO, Flask-SQLAlchemy, Flask-JWT-Extended
- **Database:** SQLite (development), PostgreSQL (planned for production)

## Run Locally

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API runs on `http://127.0.0.1:5000`.

## API Overview
| Method | Endpoint | Access |
|--------|----------|--------|
| POST | `/api/auth/register` | Public |
| POST | `/api/auth/login` | Public |
| GET | `/api/events` | Public |
| POST | `/api/events` | Organizer |
| POST | `/api/events/<id>/participants` | Logged in |
| POST | `/api/events/<id>/scores` | Organizer |
| GET | `/api/events/<id>/leaderboard` | Public |

## Roadmap
- Deployment (Render + Vercel)
- Certificate PDF download
- Analytics dashboard
- Round-wise results

## Author
Sanjay Kumar V M · [GitHub](https://github.com/SanjayKumar02-coder)