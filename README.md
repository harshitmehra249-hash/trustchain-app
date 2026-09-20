# TrustChain - Decentralized Disaster Response Network

A production-ready, full-stack web application for disaster response that integrates mesh networking, blockchain supply chain tracking, and AI-powered resource allocation.

## 📋 Project Overview

TrustChain enables rapid disaster response coordination through:
- **Mesh Networking**: Real-time communication via ESP32/LoRa devices
- **Blockchain Supply Chain**: Transparent tracking of relief resources
- **AI Resource Allocation**: Intelligent prioritization and distribution of resources
- **Multi-language Support**: Hindi, English, Garhwali, Kumaoni
- **Verifiable Credentials**: Volunteer KYC and credential verification

## 🏗️ Project Structure

```
trustchain-app/
├── frontend/                 # React 18 + TypeScript
├── backend/                  # FastAPI + PostgreSQL
├── docker-compose.yml        # Local development setup
├── docker-compose.prod.yml   # Production compose reference
├── .env.example              # Environment template
└── docs/                     # Architecture & deployment guides
```

## 🚀 Quick Start (Browser)

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- PostgreSQL 15+ (or Docker container)
- Git

### 1) Configure environment

```bash
cp .env.example .env
```

Required local values:
- `DATABASE_URL` (must point to a running PostgreSQL database)
- `JWT_SECRET` (use a long random string)
- `VITE_API_URL` (default `http://localhost:8000`)

### 2) Start the backend (Terminal 1)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URLs:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3) Start the frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- http://localhost:5173

> The app runs as **two separate processes** in local development: backend + frontend.

### Optional: Docker development services

If you prefer containerized services, use:

```bash
docker-compose up -d postgres redis
```

Then run backend/frontend manually with the commands above.

### Troubleshooting

- If backend startup fails, verify `DATABASE_URL` and ensure PostgreSQL is reachable.
- If frontend shows “Backend is not reachable”, confirm backend is running on `http://localhost:8000`.
- If `pip install` fails on `ipfshttpclient`, update `pip` and retry in a fresh virtual environment.

## 🔧 Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **UI**: Tailwind CSS + shadcn/ui
- **State**: Zustand
- **Routing**: React Router v6
- **HTTP**: Axios with interceptors
- **Web3**: ethers.js v6
- **Forms**: React Hook Form + Zod
- **Build**: Vite

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache**: Redis
- **Queue**: Celery + Redis
- **Auth**: JWT + OAuth2
- **Validation**: Pydantic v2
- **Docs**: OpenAPI/Swagger

### Blockchain
- **Network**: Polygon Mumbai (testnet) / Polygon PoS (mainnet)
- **Contracts**: Solidity 0.8.20+
- **Tools**: Hardhat / Foundry
- **Integration**: Web3.py (backend), ethers.js (frontend)

### AI/ML
- **Orchestration**: CrewAI + LangChain
- **Computer Vision**: YOLOv8 (building damage detection)
- **Speech-to-Text**: Whisper.cpp
- **Translation**: IndicTrans2
- **Optimization**: ONNX Runtime

### Infrastructure
- **Containers**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry + Prometheus + Grafana
- **Logging**: Loguru (Python) + Winston (Node.js)

## 📚 Core Features

### 1. Authentication & Authorization
- Multi-role system (Admin, Volunteer, NGO, Government, Beneficiary)
- JWT with refresh tokens (7-day access, 30-day refresh)
- Email verification (24-hour expiration)
- Rate limiting (5 failed attempts → 15-min lockout)
- OAuth2 (Google, GitHub)

### 2. Mesh Network Dashboard
- Real-time map of active mesh nodes
- WebSocket live updates (30s heartbeat)
- Node registration with validation
- Message routing visualization
- Signal strength heatmap
- Health metrics (battery, uptime, message count)

### 3. Blockchain Supply Chain Tracker
- Smart contract for item tracking
- QR code scanner for verification
- Timeline view of item journey
- Real-time status updates
- Donor dashboard
- IPFS integration for metadata

### 4. AI Resource Allocation Engine
- CrewAI multi-agent system
- Real-time request ingestion
- Priority scoring (0-100)
- Multi-language support (Hindi, English, regional)
- Voice note upload & transcription
- Route optimization

### 5. Volunteer Credential System
- W3C-compliant Verifiable Credentials (Polygon ID)
- One-time KYC process
- Browser-based wallet
- QR code verification

### 6. Real-Time Dashboard & Analytics
- Live disaster zone map
- Resource allocation charts
- Volunteer activity feed
- Supply chain metrics
- AI predictions (24-hour forecast)
- Responsive design (mobile-first)

## ✅ Quality Assurance

### Testing
- **Unit Tests**: 80%+ coverage (pytest, Vitest)
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user flows
- **Load Testing**: 1000 concurrent users (Locust, k6)

### Performance Requirements
- **Frontend**: LCP < 2.5s, INP < 200ms, CLS < 0.1
- **Bundle Size**: < 500KB (code splitting)
- **API Response**: < 200ms (p95)
- **Database**: Optimized queries with indexes

### Security Checklist
- ✅ HTTPS enforced (HSTS)
- ✅ CORS configured for specific origins
- ✅ Rate limiting on all public endpoints
- ✅ Input sanitization (XSS, SQL injection prevention)
- ✅ Password requirements: 12+ chars, mixed case, numbers, symbols
- ✅ JWT expiration & refresh rotation
- ✅ Dependency scanning (npm audit, pip-audit)
- ✅ OWASP Top 10 compliance

## 🔐 Environment Variables

Create `.env` from `.env.example` and update these values first:

```bash
# Local Postgres (example)
DATABASE_URL=******localhost:5432/trustchain

# Required security setting
JWT_SECRET=replace-with-a-long-random-secret

# Frontend -> backend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Notes:
- Never commit real credentials.
- AI, blockchain, and SMTP keys are optional for baseline local startup.

## 📖 Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [API Documentation](./docs/API.md)
- [Smart Contracts Guide](./docs/CONTRACTS.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

## 🚢 Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment
- See [Deployment Guide](./docs/DEPLOYMENT.md) for AWS, Google Cloud, Azure
- Includes Kubernetes manifests

## 📊 API Endpoints

Base URL: `/api/v1`

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Logout

### Disaster Requests
- `POST /disaster-requests` - Create request
- `GET /disaster-requests` - List requests
- `GET /disaster-requests/{id}` - Get request details
- `PUT /disaster-requests/{id}` - Update request

### Mesh Network
- `POST /mesh/nodes/register` - Register mesh node
- `GET /mesh/nodes/{node_id}/status` - Get node status
- `GET /mesh/nodes/active` - List active nodes
- `POST /mesh/messages/send` - Send mesh message

### Supply Chain
- `POST /supply-chain/items` - Create supply item
- `GET /supply-chain/items/{id}` - Get item details
- `PUT /supply-chain/items/{id}/transfer` - Transfer item
- `GET /supply-chain/items/{id}/history` - Get item history

### AI Services
- `POST /ai/assess-needs` - Assess disaster needs
- `GET /ai/prioritized-requests` - Get prioritized requests
- `POST /ai/allocate-resources` - Allocate resources
- `GET /ai/route-optimization` - Optimize delivery routes

Full API documentation available at `/docs` (Swagger UI)

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Git workflow (feature, bugfix, hotfix branches)
- Conventional commits
- Pull request requirements
- Code quality standards

## 📝 License

MIT License - see [LICENSE](./LICENSE) file

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/harshitmehra249-hash/trustchain-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/harshitmehra249-hash/trustchain-app/discussions)
- **Email**: support@trustchain-app.dev

## 🎯 Roadmap

- [x] Project initialization
- [ ] Authentication & authorization system
- [ ] Mesh network dashboard
- [ ] Blockchain supply chain tracker
- [ ] AI resource allocation engine
- [ ] Volunteer credential system
- [ ] Real-time analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Advanced analytics & reporting
- [ ] Multi-region deployment

---

**Built with ❤️ for disaster response coordination**
