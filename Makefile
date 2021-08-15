.PHONY:\
	run-all\
	run\
	down\
	test\

run-all:
	docker-compose up -d

run:
	docker-compose up -d mongo mongo-express
	poetry run python ./discord_pigeon/main.py

manual:
	docker-compose up -d mongo mongo-express
	poetry run python ./discord_pigeon/main.py -m
	docker-compose up -d discord-pigeon
	poetry run python ./discord_pigeon/main.py -l

down:
	docker-compose down

clean:
	docker rmi -f discord-pigeon

test:
	poetry run pytest tests