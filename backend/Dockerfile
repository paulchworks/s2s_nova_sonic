FROM python:3.13-alpine

WORKDIR /app

# Ensure entrypoint.sh exists in the build context
COPY . ./

# Install dependencies (include bash only if needed)
RUN apk add --update jq curl py-pip inotify-tools && \
    pip install --no-cache-dir -r requirements.txt

# Fix script permissions and line endings
RUN chmod +x entrypoint.sh

# Use correct path: /app/entrypoint.sh (via WORKDIR)
ENTRYPOINT ["./entrypoint.sh"]