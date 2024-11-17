# My Personal Stock Evaluator

## Build Docker image and start the container
```shell
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose up --build -d && docker-compose logs -f
```

Access the [Web UI](http://localhost:8051)


## What's next
- local DB for my stocks to watch (CRUD) and a page for displaying a list of the stocks with DCF
- alternative stock evaluation methods