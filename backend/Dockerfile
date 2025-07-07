FROM python:3.13-alpine

WORKDIR /app

# Copy all backend files
COPY . .

# Ensure proper shell style & execution permissions
# - Converts CRLF to LF using sed if needed
# - Makes the script executable
RUN sed -i 's/\r$//' entrypoint.sh \
 && chmod +x entrypoint.sh \
 && ls -l entrypoint.sh \
 && head -n 1 entrypoint.sh

# Install OS dependencies
RUN apk add --no-cache jq curl py-pip inotify-tools

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose WebSocket and MCP ports
EXPOSE 80
EXPOSE 8000

# Default environment settings
ENV LOGLEVEL=INFO
ENV MCP_PORT=8000

ENTRYPOINT ["./entrypoint.sh"]
