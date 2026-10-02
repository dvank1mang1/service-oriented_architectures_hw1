.PHONY: test run docker-up docker-down health

test:
	python3 -m unittest discover -s tests -v

run:
	python3 -m src.catalog_service

docker-up:
	docker compose up --build -d --wait

docker-down:
	docker compose down

health:
	curl --fail --silent --show-error http://localhost:8080/health
