# import multiprocessing

# Bind to the appropriate host and port
bind = "0.0.0.0:8000"

# Number of worker processes
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 2

# Use 'uvicorn.workers.UvicornWorker' to run FastAPI with Gunicorn
worker_class = "uvicorn.workers.UvicornWorker"

worker_tmp_dir = "/dev/shm"

# Log level
loglevel = "info"

# Access log file
accesslog = "-"

# Error log file
errorlog = "-"

# Timeout for requests
timeout = 30 