# --------- Base Stage ---------
    FROM python:3.10.12-slim AS base

    # Set working directory
    WORKDIR /code
    
    # Install essential build tools
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*
    
    # Ensure Python-installed binaries like arq are accessible
    ENV PATH="/usr/local/bin:$PATH"
    
    # --------- Requirements Stage ---------
    FROM base AS requirements-stage
    
    # Install a compatible version of Poetry
    ENV POETRY_VERSION=1.8.4
    RUN pip install poetry==${POETRY_VERSION}
    
    # Copy Poetry configuration
    WORKDIR /tmp
    COPY ./pyproject.toml ./poetry.lock* /tmp/
    
    # Export dependencies to requirements.txt
    RUN poetry export --without-hashes --no-interaction --no-ansi -f requirements.txt -o requirements.txt
    
    # --------- Builder Stage ---------
    FROM base AS builder
    
    # Copy the exported requirements
    COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
    
    # Install dependencies
    RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
    
    # Copy application code
    COPY ./src /code/src
    
    # --------- Final Image ---------
    FROM base AS final
    
    # Copy dependencies from the builder
    COPY --from=builder /usr/local /usr/local
    
    # Copy application code
    COPY ./src /code/src
    
    # Copy wait-for-it script
    COPY wait-for-it.sh /code/wait-for-it.sh
    RUN chmod +x /code/wait-for-it.sh
    
    # Expose application port
    EXPOSE 8000
    
    # Default command for development
    CMD ["/code/wait-for-it.sh", "db:5432", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]