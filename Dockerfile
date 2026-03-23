FROM python:3.12-slim

# Run as non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install Poetry
RUN pip install --no-cache-dir --user poetry
ENV PATH="/home/appuser/.local/bin:$PATH"

# Copy project metadata first (layer caching)
COPY --chown=appuser pyproject.toml poetry.lock ./

# Install dependencies only (no dev deps)
RUN poetry install --only main --no-root --no-interaction

# Copy application code
COPY --chown=appuser semitone_api/ ./semitone_api/

# Install the project itself
RUN poetry install --only main --no-interaction

EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "semitone_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
