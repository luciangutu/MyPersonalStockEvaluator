Build Docker image
```shell
docker build -t stock_valuator .
```


Start the container
```shell
docker run -d -p 8051:8051 stock_valuator --name stock_valuator
```