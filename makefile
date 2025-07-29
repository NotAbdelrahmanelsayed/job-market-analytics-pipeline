## ------------------------
## Container management
## ------------------------
up-build:
	docker compose up -d --build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

reset: # DANGER: Will remove everything in docker images,volumes and even networks
	docker compose down -v
	docker system prune -fa --volumes
	docker compose up -d --build

## ------------------------
## Shell Access
## ------------------------
sh: ## Access app-dev shell
	docker exec -it app-dev /bin/bash


## ------------------------
## Scrapy Commands
## ------------------------

startproject:
	scrapy startproject extract

genspider:
	scrapy genspider spider https://dataengjobs.com/

fetch:
	scrapy fetch --nolog 'https://dataengjobs.com/' > response.html

crawl:
	scrapy crawl data_eng_job -o output.json