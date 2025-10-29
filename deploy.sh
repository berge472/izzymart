#!/bin/bash

# IzzyMart Deployment Script
# This script builds Docker images and deploys to Kubernetes using Helm

set -e

# Configuration
DOCKER_REGISTRY="berge472"
API_IMAGE="${DOCKER_REGISTRY}/izzymart-api"
GUI_IMAGE="${DOCKER_REGISTRY}/izzymart-gui"
VERSION="${1:-latest}"
NAMESPACE="izzymart"

echo "========================================"
echo "IzzyMart Deployment Script"
echo "========================================"
echo "Version: ${VERSION}"
echo "Namespace: ${NAMESPACE}"
echo "========================================"

# Build API image
echo ""
echo "Building API image..."
cd api
docker build -t ${API_IMAGE}:${VERSION} . 
echo "✓ API image built successfully"

# Build GUI image
echo ""
echo "Building GUI image..."
cd ../gui
docker build -t ${GUI_IMAGE}:${VERSION} . --no-cache
echo "✓ GUI image built successfully"

# Push images
echo ""
read -p "Push images to Docker Hub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Pushing API image..."
    docker push ${API_IMAGE}:${VERSION}
    echo "✓ API image pushed"

    echo "Pushing GUI image..."
    docker push ${GUI_IMAGE}:${VERSION}
    echo "✓ GUI image pushed"
else
    echo "Skipping image push"
fi

# Deploy with Helm
echo ""
read -p "Deploy to Kubernetes using Helm? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    cd ../helm

    # Check if release exists
    if helm list -n ${NAMESPACE} | grep -q "izzymart"; then
        echo "Upgrading existing Helm release..."
        helm upgrade izzymart . \
            --namespace ${NAMESPACE} \
            --set image.api.tag=${VERSION} \
            --set image.gui.tag=${VERSION} \
            --wait
        echo "✓ Helm release upgraded"
    else
        echo "Installing new Helm release..."
        helm install izzymart . \
            --namespace ${NAMESPACE} \
            --create-namespace \
            --set image.api.tag=${VERSION} \
            --set image.gui.tag=${VERSION} \
            --wait
        echo "✓ Helm release installed"
    fi

    echo ""
    echo "Deployment complete!"
    echo ""
    echo "To view the pods:"
    echo "  kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=izzymart"
    echo ""
    echo "To view the services:"
    echo "  kubectl get svc -n ${NAMESPACE} -l app.kubernetes.io/instance=izzymart"
    echo ""
    echo "To access the GUI (port-forward):"
    echo "  kubectl port-forward -n ${NAMESPACE} svc/izzymart-gui 8080:80"
else
    echo "Skipping Helm deployment"
fi

echo ""
echo "Done!"
