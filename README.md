# My Personal Stock Evaluator

## Setup

### API Key Configuration
1. Get your free API key from [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs)
2. Open `config.py` and replace `YOUR_API_KEY_HERE` with your actual API key

### Build Docker image and start the container
```shell
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose up --build -d && docker compose logs -f
```

Access the [Web UI](http://localhost:8051)


## What's next
- alternative stock evaluation methods to DCF
- metrics evaluation
- key metrics page