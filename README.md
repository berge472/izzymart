# IzzyMart Self-Checkout System

A complete self-checkout kiosk system with Vue3 frontend, FastAPI backend, and MongoDB database. Features barcode scanning, product lookup via multiple APIs, and a touch-friendly interface.

## Features

- **Barcode Scanner Support**: Automatic detection of HID barcode scanners
- **Multi-Source Product Lookup**:
  - OpenFoodFacts API for nutrition data
  - Amazon search for pricing and images
  - Google Images as fallback
- **Touch-Friendly UI**: Large buttons and on-screen keyboard
- **Shopping Cart Management**: Add, remove, and manage items
- **Real-Time Product Search**: Search products by name
- **Containerized**: Docker and Kubernetes ready

## Architecture

```
┌─────────────────────────────────────────┐
│           Vue3 Frontend (GUI)            │
│  - Vuetify UI Components                │
│  - Pinia State Management               │
│  - Barcode Scanner Detection            │
│  - On-Screen Keyboard                   │
└─────────────────┬───────────────────────┘
                  │ HTTP API
┌─────────────────▼───────────────────────┐
│         FastAPI Backend (API)            │
│  - Product Lookup Service               │
│  - Authentication (JWT)                  │
│  - Image Processing                      │
│  - Web Scraping (Playwright)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           MongoDB Database               │
│  - Product Cache                         │
│  - Image Storage (GridFS)               │
│  - Transaction History                   │
└─────────────────────────────────────────┘
```

## Quick Start

### Option 1: Docker Compose (Recommended for Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Access the application at:
- GUI: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

```bash
cd api
pip install -r requirements.txt
python -m playwright install chromium
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

```bash
cd gui
npm install
npm run serve
```

### Option 3: Kubernetes Deployment

```bash
# Build and push images
./deploy.sh v1.0.0 production

# Or manually:
cd api && docker build -t berge472/izzymart-api:v1.0.0 .
cd ../gui && docker build -t berge472/izzymart-gui:v1.0.0 .
docker push berge472/izzymart-api:v1.0.0
docker push berge472/izzymart-gui:v1.0.0

# Deploy with Helm
helm install izzymart ./helm \
  --namespace izzymart \
  --create-namespace \
  --set image.api.tag=v1.0.0 \
  --set image.gui.tag=v1.0.0
```

See [helm/README.md](helm/README.md) for detailed Helm chart documentation.

## Project Structure

```
izzymart/
├── api/                    # FastAPI backend
│   ├── api/
│   │   ├── product/       # Product lookup service
│   │   ├── files/         # File/image management
│   │   └── user/          # User authentication
│   ├── config/            # Configuration
│   ├── Dockerfile         # API container image
│   └── requirements.txt   # Python dependencies
├── gui/                   # Vue3 frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── store/         # Pinia stores
│   │   ├── services/      # API client
│   │   └── views/         # Page views
│   ├── Dockerfile         # GUI container image
│   ├── nginx.conf         # Nginx configuration
│   └── package.json       # Node dependencies
├── helm/                  # Kubernetes Helm chart
│   ├── templates/         # K8s manifests
│   ├── Chart.yaml         # Chart metadata
│   ├── values.yaml        # Default values
│   └── README.md          # Helm documentation
├── docker-compose.yml     # Local development setup
├── deploy.sh              # Deployment script
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Get JWT token
- `POST /api/v1/auth/register` - Register new user

### Products
- `GET /api/v1/products/upc/{upc}` - Lookup product by UPC barcode
- `GET /api/v1/products/search` - Search products by name
- `GET /api/v1/products` - List all products
- `POST /api/v1/products/reset` - Clear product cache

### Files
- `GET /api/v1/files/{file_id}` - Download file by ID
- `POST /api/v1/files/upload` - Upload file

Full API documentation available at `/docs` endpoint.

## Environment Variables

### API

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_HOST` | MongoDB hostname | `localhost` |
| `MONGO_PORT` | MongoDB port | `27017` |
| `MONGO_DB_NAME` | Database name | `izzymart` |
| `JWT_SECRET` | JWT signing secret | (required) |
| `JWT_EXPIRE_MINUTES` | Token expiration | `10080` (7 days) |

### GUI

| Variable | Description | Default |
|----------|-------------|---------|
| `VUE_APP_API_URL` | Backend API URL | `http://localhost:8000` |

## Hardware Requirements

### Kiosk Setup

- **Touch Screen Display**: 1920x1080 recommended
- **Barcode Scanner**: USB HID device (keyboard emulation mode)
- **Computer**: Any device capable of running a web browser
  - Raspberry Pi 4 (4GB RAM minimum)
  - Intel NUC
  - Standard PC/Desktop

### Server Requirements

- **Production**:
  - CPU: 2+ cores
  - RAM: 4GB minimum (8GB recommended)
  - Storage: 20GB minimum for Docker images and data

## Barcode Scanner Configuration

The system automatically detects barcode scanner input by monitoring for rapid number key presses (< 100ms between keys).

Requirements:
- Scanner must be in HID keyboard emulation mode
- Must send at least 8 digits
- Should send ENTER key after barcode (optional)

Tested scanners:
- Honeywell Voyager 1200g
- Symbol LS2208
- Generic USB barcode scanners

## Development

### Running Tests

```bash
# Backend tests
cd api
pytest

# Frontend tests
cd gui
npm run test:unit
```

### Code Style

```bash
# Backend (Python)
cd api
black .
flake8 .

# Frontend (TypeScript/Vue)
cd gui
npm run lint
```

## Production Deployment Checklist

- [ ] Change default JWT secret in Helm values
- [ ] Configure proper domain in ingress
- [ ] Enable HTTPS/TLS with cert-manager
- [ ] Set up MongoDB authentication
- [ ] Configure MongoDB backups
- [ ] Set resource limits based on load testing
- [ ] Use specific image tags (not `latest`)
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation
- [ ] Configure horizontal pod autoscaling
- [ ] Test barcode scanner compatibility

## Troubleshooting

### Barcode Scanner Not Working

1. Verify scanner is in HID keyboard mode
2. Check that scanner sends at least 8 digits
3. Test scanner in a text editor - should type numbers
4. Check browser console for scanner events

### Product Images Not Loading

1. Check API logs for Playwright errors
2. Verify Chromium is installed: `python -m playwright install chromium`
3. Check network connectivity to image sources
4. Review CORS configuration in nginx

### Database Connection Issues

1. Verify MongoDB is running: `docker ps` or `kubectl get pods`
2. Check environment variables (MONGO_HOST, MONGO_PORT)
3. Review MongoDB logs for errors
4. Test connection: `mongosh mongodb://localhost:27017/izzymart`

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Email: [Your Email]

## Acknowledgments

- OpenFoodFacts for nutrition data API
- Playwright for web automation
- Vue.js and Vuetify for the UI framework
