.PHONY: help build up down logs clean restart

help:
	@echo "📋 SkillFit AI Docker Commands"
	@echo "make build  - Build all images"
	@echo "make up     - Start all services"
	@echo "make down   - Stop all services"
	@echo "make logs   - View logs"
	@echo "make clean  - Remove containers and volumes"
	@echo "make restart - Restart all services"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Frontend: http://localhost:8501"
	@echo "✅ Backend: http://localhost:8000"
	@echo "✅ API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

restart: down up