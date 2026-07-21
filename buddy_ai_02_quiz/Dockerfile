# ==========================================
# Stage 1: Build environment
# ==========================================
FROM python:3.12-slim AS builder

# Instalar uv directamente
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Crear el entorno virtual limpio
RUN uv venv /opt/venv

# Copiar archivos de configuración de dependencias de la raíz
COPY pyproject.toml uv.lock* ./

# Instalar las dependencias del proyecto usando la definición del pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv -r pyproject.toml

# ==========================================
# Stage 2: Final lightweight runtime
# ==========================================
FROM python:3.12-slim
WORKDIR /app

# Copiar el entorno virtual aislado desde la etapa build
COPY --from=builder /opt/venv /opt/venv

# Configurar rutas del sistema
ENV PATH="/opt/venv/bin:$PATH"

# Copiar todas tus configuraciones y código al contenedor
COPY src/ /app/src/
COPY config/ /app/config/
COPY pyproject.toml /app/

# Ejecutar usando la función run definida en tu archivo main
CMD ["python", "-m", "src.main"]
