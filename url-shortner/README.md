# URL Shortener

## Run the application

```powershell
docker-compose up --build
```

The API is available at `http://127.0.0.1:5000`.

## Run the tests in Docker

The test stack uses disposable PostgreSQL and Redis containers and does not use
the development database.

```powershell
docker-compose -p url-shortner-tests -f docker-compose.test.yml up --build `
  --abort-on-container-exit --exit-code-from tests
docker-compose -p url-shortner-tests -f docker-compose.test.yml down --volumes
```

The first command returns the pytest exit code, making it suitable for CI. The
second command removes only the isolated test containers and their temporary
data.

## Example request

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/shorten `
  -ContentType application/json `
  -Body '{"url":"https://www.google.com"}'
```
