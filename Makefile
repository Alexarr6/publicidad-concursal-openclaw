.PHONY: docker-build docker-help docker-export docker-shell

docker-build:
	docker build -t publicidadconcursal-exporter:local .

docker-help:
	docker compose run --rm app --help

docker-export:
	docker compose run --rm app --date $${DATE} --output-dir /app

docker-shell:
	docker compose run --rm --entrypoint sh app
