# Resilient Routes

A web-based platform for seismic reliability assessment of transportation networks in the United States. The application enables interactive selection of infrastructure components (bridges, roads) and execution of custom earthquake scenarios to calculate bridge failure probabilities. Feel free to read more [here](https://arxiv.org/pdf/2210.06404).

## Technologies Used

- Frontend: React, TypeScript
- Backend: FastAPI, Python
- Deployment: AWS EC2, Vercel
- Libraries: pandas, numpy, scipy, asyncio, playwright, pydantic

## Getting Started

### Prerequisites

- Python 3.x
- Node.js and npm
- pip

### Installation

**1. Set up the Python virtual environment:**

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

**2. Install frontend dependencies:**

```bash
cd frontend/
npm install
```

### Running the Application

**Start the frontend:**

```bash
cd frontend/
npm run dev
```

**Start the backend** (in a separate terminal):

```bash
cd backend/
python3 main.py
```

The application should now be running locally on your machine.
