# Dockerfile para Conservas del Mundo
FROM python:3.11-slim

WORKDIR /app

# Instalar uv
RUN pip install --no-cache-dir uv

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias del proyecto
RUN uv sync --frozen --no-dev

# Copiar código fuente
COPY . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Si no existe data/build.db, el entrypoint genera la base de datos
ENTRYPOINT ["./docker-entrypoint.sh"]

# Exponer el puerto 8000
EXPOSE 8000
