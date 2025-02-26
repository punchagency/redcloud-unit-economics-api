# Nigeria Retail Economics API

A FastAPI-based REST API for accessing retail economic data and metrics for Nigerian cities.

## Features

- City-level retail metrics and statistics
- Caching with Redis for improved performance
- BigQuery integration for data storage and queries
- Environment-based configuration
- CORS support

## Prerequisites

- Python 3.8+
- Redis server
- Google Cloud Platform account with BigQuery enabled
- Google Cloud service account credentials

## Local Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/nigeria-retail-economics-api.git
cd nigeria-retail-economics-api
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
```

5. Run the development server:

```bash
uvicorn app.main:app --reload
```

Development

```bash
uvicorn app.main:app --reload
```

Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

The API is documented with Swagger UI at:

`http://localhost:8000/docs`

## Deployment

The API is containerized and can be deployed using Docker.

## Performance Considerations

- Redis caching is implemented for all endpoints
- BigQuery queries are optimized with proper indexing
- Connection pooling is used for both Redis and BigQuery
- Retry logic is implemented for BigQuery queries

## Contributing

1. Clone the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)

