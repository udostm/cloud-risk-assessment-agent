DOCKER=podman

.PHONY: gen_config scan import_db

build:
	${DOCKER} compose build

gen_config:
	${DOCKER} compose run -it --rm agent python src/config/gen_scan_config.py

shell:
	${DOCKER} compose run -it --rm agent /bin/bash

scan:
	${DOCKER} compose run -it --rm agent python src/scan/scan_resource.py
	
	${DOCKER} compose run -it --rm agent python src/scan/scan_import.py

import_db:
	${DOCKER} compose run -it --rm agent mkdir -p /sqlite
	${DOCKER} compose run -it --rm agent chmod 777 /sqlite
	${DOCKER} compose run -it --rm agent python scripts/gen_db
	${DOCKER} compose run -it --rm agent python src/scan/scan_import.py

sample:
	${DOCKER} compose down
	${DOCKER} compose run --rm agent python scripts/sample_import
	sync
	${DOCKER} compose down
	${DOCKER} compose up -d

run:
	${DOCKER} compose build
	${DOCKER} compose up -d

stop:
	${DOCKER} compose stop

down:
	${DOCKER} compose down

refresh:
	@echo "Refreshing database with user-based confirmation..."
	${DOCKER} compose run -it --rm agent mkdir -p /sqlite
	${DOCKER} compose run -it --rm agent chmod 777 /sqlite
	${DOCKER} compose run -it --rm agent python src/db/db_refresh.py
