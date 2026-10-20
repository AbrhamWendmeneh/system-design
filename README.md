# System Design Practice

This repository contains hands-on system design projects. Each folder explores
one system independently, including its architecture, implementation,
infrastructure, and automated tests.

## Projects

| Project | Description | Technologies |
| --- | --- | --- |
| [URL Shortener](./url-shortner/) | Generates compact URLs, persists mappings, caches redirects, and returns HTTP redirects. | Python, Flask, PostgreSQL, Redis, Docker, pytest |

## Repository structure

```text
system-design/
├── README.md
└── url-shortner/
    ├── app/
    ├── docker-compose.yml
    ├── docker-compose.test.yml
    └── README.md
```

Every project should remain self-contained and include:

- A README describing the requirements and design decisions
- Application and infrastructure configuration
- Automated tests
- Commands for running the application locally
- Notes about scaling, reliability, and future improvements

## Running the URL shortener

```powershell
cd url-shortner
docker-compose up --build
```

The API will be available at `http://127.0.0.1:5000`.

Run its isolated Docker test suite with:

```powershell
docker-compose -p url-shortner-tests -f docker-compose.test.yml up --build `
  --abort-on-container-exit --exit-code-from tests
docker-compose -p url-shortner-tests -f docker-compose.test.yml down --volumes
```

See the [URL shortener documentation](./url-shortner/README.md) for request
examples and project-specific instructions.

## Learning goals

The projects in this repository focus on practical design concerns such as:

- API and data-model design
- Caching and persistence
- Horizontal scaling and fault tolerance
- Consistency and availability trade-offs
- Observability and operational readiness
- Repeatable testing with isolated infrastructure

## Planned projects

- Rate limiter
- Distributed cache
- Notification service
- Chat system
- File storage service

