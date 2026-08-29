COMPOSE = docker compose --env-file docker/build.env --env-file .env -f docker/compose.yaml

.PHONY: up postgres-up postgres-stop postgres-logs simulator-up simulator-stop ps down-v

up:
	$(COMPOSE) up -d

postgres-up:
	$(COMPOSE) up -d postgres

postgres-stop:
	$(COMPOSE) stop postgres

postgres-logs:
	$(COMPOSE) logs -f postgres

simulator-up:
	$(COMPOSE) up -d simulator

simulator-stop:
	$(COMPOSE) stop simulator

ps:
	$(COMPOSE) ps

down-v:
	$(COMPOSE) down -v