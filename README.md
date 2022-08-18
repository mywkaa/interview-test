build docker image:
```
docker build -t yousician-test:latest .
```

run application:
```
docker run -p 5000:5000 -ti --rm --name=yousician-test-interview yousician-test:latest
```

upload fixtures:
```
docker exec -ti yousician-test-interview python /app/upload_fixtures.py
```
