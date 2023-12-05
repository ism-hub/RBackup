.PHONY: test_backup_manager test_cron_script build

all: test_backup_manager test_cron_script

build:
	docker compose -f test_container_compose_file.yaml build

test_backup_manager: build
	docker compose -f test_container_compose_file.yaml run test_container bash -c 'PYTHONPATH=/RBackup/src/:/RBackup/config/ pytest --log-cli-level=10 -xvvs /RBackup/tests/test_backup_manager/*'

test_cron_script: build
	docker compose -f test_container_compose_file.yaml run test_container bash -c 'PYTHONPATH=/RBackup/src/:/RBackup/config/:/RBackup pytest --log-cli-level=10 -xvvs /RBackup/tests/test_cron_script/*'
