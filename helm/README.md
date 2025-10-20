# IzzyMart Helm Chart

This Helm chart deploys the IzzyMart self-checkout system on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Persistent Volume provisioner support in the underlying infrastructure (for MongoDB persistence)

## Components

- **API**: FastAPI backend service for product lookups and cart management
- **GUI**: Vue3 frontend for the self-checkout interface
- **MongoDB**: Database for product and transaction storage

## Installation

### 1. Build and Push Docker Images

First, build and push the Docker images to Docker Hub:

```bash
# Build and push API image
cd api
docker build -t berge472/izzymart-api:latest .
docker push berge472/izzymart-api:latest

# Build and push GUI image
cd ../gui
docker build -t berge472/izzymart-gui:latest .
docker push berge472/izzymart-gui:latest
```

### 2. Configure Cloudflare Tunnel (Optional)

If using Cloudflare Tunnel to expose your application:

```bash
# Install cloudflared in your cluster
# See: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/

# Create a tunnel
cloudflared tunnel create izzymart

# Configure the tunnel to route to your ingress
# Add to your cloudflared config:
# ingress:
#   - hostname: izzymart.app
#     service: http://izzymart-gui.izzymart.svc.cluster.local:80
```

### 3. Install the Helm Chart

```bash
# Install with default values (uses izzymart.app)
helm install izzymart ./helm

# Install with custom values
helm install izzymart ./helm -f custom-values.yaml

# Install in a specific namespace
helm install izzymart ./helm --namespace izzymart --create-namespace
```

### 4. Upgrade the Deployment

```bash
# Upgrade to new version
helm upgrade izzymart ./helm

# Upgrade with new values
helm upgrade izzymart ./helm -f custom-values.yaml
```

### 5. Uninstall

```bash
helm uninstall izzymart
```

## Configuration

The following table lists the configurable parameters and their default values.

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount.api` | Number of API replicas | `1` |
| `replicaCount.gui` | Number of GUI replicas | `2` |
| `replicaCount.mongodb` | Number of MongoDB replicas | `1` |

### Image Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.api.repository` | API image repository | `berge472/izzymart-api` |
| `image.api.tag` | API image tag | `latest` |
| `image.gui.repository` | GUI image repository | `berge472/izzymart-gui` |
| `image.gui.tag` | GUI image tag | `latest` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.api.type` | API service type | `ClusterIP` |
| `service.api.port` | API service port | `8000` |
| `service.gui.type` | GUI service type | `ClusterIP` |
| `service.gui.port` | GUI service port | `80` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `""` (uses default) |
| `ingress.hosts[0].host` | Hostname | `izzymart.app` |

**Note**: The default configuration is optimized for Cloudflare Tunnel. TLS is handled by Cloudflare, so no ingress TLS configuration is needed.

### MongoDB Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mongodb.persistence.enabled` | Enable persistence | `true` |
| `mongodb.persistence.size` | Persistent volume size | `10Gi` |
| `mongodb.persistence.storageClass` | Storage class | `""` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.api.enabled` | Enable API autoscaling | `false` |
| `autoscaling.gui.enabled` | Enable GUI autoscaling | `true` |
| `autoscaling.gui.minReplicas` | Minimum GUI replicas | `2` |
| `autoscaling.gui.maxReplicas` | Maximum GUI replicas | `10` |

## Example Custom Values

Create a `custom-values.yaml` file:

```yaml
ingress:
  enabled: true
  hosts:
    - host: checkout.mystore.com
      paths:
        - path: /api
          pathType: Prefix
          backend: api
        - path: /
          pathType: Prefix
          backend: gui
  tls:
    - secretName: mystore-tls
      hosts:
        - checkout.mystore.com

config:
  api:
    rootPassword: "my-secure-admin-password"
    jwtSecret: "my-super-secret-key-change-me"

resources:
  api:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 1000m
      memory: 2Gi

mongodb:
  persistence:
    enabled: true
    size: 50Gi
    storageClass: "fast-ssd"
```

Then install with:

```bash
helm install izzymart ./helm -f custom-values.yaml
```

## Accessing the Application

### With Cloudflare Tunnel (Default)

The application is configured to be served at `izzymart.app` through Cloudflare Tunnel. After deploying:

1. Access your application at: **https://izzymart.app**
2. API endpoint: **https://izzymart.app/api**

### Local Development (Port Forward)

For local testing without Cloudflare Tunnel:

```bash
# Port forward the GUI service
kubectl port-forward svc/izzymart-gui 8080:80

# Access at http://localhost:8080
```

## Monitoring

Check pod status:

```bash
kubectl get pods -l app.kubernetes.io/instance=izzymart
```

View API logs:

```bash
kubectl logs -l app.kubernetes.io/component=api -f
```

View GUI logs:

```bash
kubectl logs -l app.kubernetes.io/component=gui -f
```

View MongoDB logs:

```bash
kubectl logs -l app.kubernetes.io/component=mongodb -f
```

## Troubleshooting

### Pods not starting

Check pod status and events:

```bash
kubectl describe pod <pod-name>
```

### Database connection issues

Verify MongoDB is running:

```bash
kubectl get pods -l app.kubernetes.io/component=mongodb
kubectl logs -l app.kubernetes.io/component=mongodb
```

### Image pull errors

Ensure Docker images are built and pushed:

```bash
docker images | grep izzymart
```

## Security Notes

**IMPORTANT**: Before deploying to production:

1. **Change the root admin password** in `values.yaml`:
   ```yaml
   config:
     api:
       rootPassword: "use-a-strong-password-here"
   ```
   This password is used for logging into the admin panel at `/admin`.

2. Change the default JWT secret in `values.yaml`:
   ```yaml
   config:
     api:
       jwtSecret: "use-a-strong-random-secret-here"
   ```

3. If not using Cloudflare Tunnel, enable TLS/HTTPS via ingress with cert-manager

4. Consider enabling MongoDB authentication

5. Review and adjust resource limits based on your workload

6. Use a specific image tag instead of `latest` for production deployments

## Admin Access

To access the admin panel:

1. Navigate to **https://your-domain.com/admin** (e.g., https://izzymart.app/admin)
2. Login with:
   - **Username**: `root`
   - **Password**: The password you set in `config.api.rootPassword` (default: `changeme-in-production`)

The admin panel allows you to:
- Scan products and edit their details
- Upload/manage product images
- Delete products from the database
