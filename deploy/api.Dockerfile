FROM python:3.11-slim-bookworm
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e ".[api]"
ENV EVIDENCE_ROOT=/evidence
EXPOSE 8000
CMD ["uvicorn", "coflow5.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
