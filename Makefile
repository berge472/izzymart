.PHONY: mongo mongo-stop mongo-clean help

# MongoDB configuration
MONGO_CONTAINER_NAME=izzymart-mongo
MONGO_PORT=27017
MONGO_VERSION=latest
MONGO_DATA_DIR=./mongo-data

help:
	@echo "Available targets:"
	@echo "  make mongo       - Start MongoDB container"
	@echo "  make mongo-stop  - Stop MongoDB container"
	@echo "  make mongo-clean - Stop and remove MongoDB container and data"
	@echo "  make help        - Show this help message"

mongo:
	@echo "Starting MongoDB container..."
	@docker run -d \
		--name $(MONGO_CONTAINER_NAME) \
		-p $(MONGO_PORT):27017 \
		-v $(MONGO_DATA_DIR):/data/db \
		-e MONGO_INITDB_DATABASE=app \
		--restart unless-stopped \
		mongo:$(MONGO_VERSION)
	@echo "MongoDB is running on localhost:$(MONGO_PORT)"
	@echo "Container name: $(MONGO_CONTAINER_NAME)"
	@echo "Database name: app"

mongo-stop:
	@echo "Stopping MongoDB container..."
	@docker stop $(MONGO_CONTAINER_NAME)
	@echo "MongoDB container stopped"

mongo-clean:
	@echo "Stopping and removing MongoDB container..."
	@docker stop $(MONGO_CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(MONGO_CONTAINER_NAME) 2>/dev/null || true
	@echo "Removing MongoDB data directory..."
	@rm -rf $(MONGO_DATA_DIR)
	@echo "MongoDB container and data removed"
