ENV = dev
WEB_CONTAINER_NAME = tester_web
EXEC_PREFIX = docker exec -it $(WEB_CONTAINER_NAME)
MANAGEMENT_PREFIX = $(EXEC_PREFIX) bash -c "python manage.py

DOCKER_COMPOSE = docker-compose -f docker-compose.yml
BUILD = $(DOCKER_COMPOSE) build
DOWN_ALL = $(DOCKER_COMPOSE) down -v

MAKE_MIGRATIONS = $(MANAGEMENT_PREFIX) makemigrations"
APPLY_MIGRATIONS = $(MANAGEMENT_PREFIX) migrate"
SEED_DB = $(EXEC_PREFIX) python -m _db_seed


build:
	$(BUILD)
run:
	$(DOCKER_COMPOSE) up
run-d:
	$(DOCKER_COMPOSE) up -d
stop:
	$(DOCKER_COMPOSE) stop
down-all:
	$(DOWN_ALL)
clean-build: down-all
	$(MAKE) build
clean-run: clean-build
	$(MAKE) run

migrations:
	$(MAKE_MIGRATIONS)
	
apply-migrations:
	
	$(APPLY_MIGRATIONS)
seed-db:
	
	$(SEED_DB)

full-run:
	$(MAKE) down-all
	$(MAKE) run-d
	sleep 5
	$(MAKE) apply-migrations
	$(MAKE) seed-db

logs:
	docker logs -f $(WEB_CONTAINER_NAME)

restart:
	$(DOCKER_COMPOSE) restart