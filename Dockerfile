HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/api/health/')"

# Run with Gunicorn
# Shell form (not exec form) is required so $PORT is expanded at runtime.
# Render's Dockerfile builder runs CMD without a shell otherwise, so an exec-form
# array would pass the literal string "$PORT" to gunicorn instead of the real port,
# causing an immediate crash and failed healthchecks.
CMD gunicorn crm_backend.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
