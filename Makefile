.PHONY: gen_config scan import_db

build:
	docker compose build

gen_config:
	docker compose run -it --rm agent python src/config/gen_scan_config.py

shell:
	docker compose run -it --rm agent /bin/bash

scan:
	docker compose run -it --rm agent python src/scan/scan_resource.py
	
	docker compose run -it --rm agent python src/scan/scan_import.py

import_db:
	docker compose run -it --rm agent mkdir -p /sqlite
	docker compose run -it --rm agent chmod 777 /sqlite
	docker compose run -it --rm agent python scripts/gen_db
	docker compose run -it --rm agent python src/scan/scan_import.py

sample:
	docker compose down
	docker compose run -it --rm agent python scripts/sample_import
	sync
	docker compose down
	docker compose up -d

run:
	docker compose build
	docker compose up -d

stop:
	docker compose stop

down:
	docker compose down

refresh:
	@echo "Refreshing database with user-based confirmation..."
	docker compose run -it --rm agent mkdir -p /sqlite
	docker compose run -it --rm agent chmod 777 /sqlite
	docker compose run -it --rm agent python src/db/db_refresh.py
