# CodeLeap Project for Back-end developer

This project implements a Django-based API for managing posts, including basic CRUD operations. The API is designed using Django Rest Framework (DRF) and is dockerized for easy deployment.

## Features

- List, create, retrieve, update (partial), and delete posts
- Dockerized for easy deployment

## Getting Started

### Prerequisites

- Python
- Django
- Django Rest Framework
- Docker

### Installation

### Copy environment file

```shell script
cp packaging/env.txt .env
```
If needed, fill in the values in .env file

### Run project

```shell script
make build
```
```shell script
make run
```

### Apply database migrations in a separate terminal tab

```sh
make apply-migrations
```