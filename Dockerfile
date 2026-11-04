FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl xvfb libxcb-util1 libxkbcommon-x11-0 libglu1-mesa \
    libgl1 libegl1 libfontconfig1 libfreetype6 libxrender1 libxi6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L --fail -o /tmp/oda.deb \
    'https://www.opendesign.com/guestfiles/get?filename=ODAFileConverter_QT6_lnxX64_11dll.deb' \
    && dpkg -i /tmp/oda.deb || apt-get update && apt-get install -f -y \
    && rm -f /tmp/oda.deb \
    && BIN="$(find / -type f -name ODAFileConverter -perm -111 2>/dev/null | head -1)" \
    && test -n "$BIN" && ln -sf "$BIN" /usr/local/bin/ODAFileConverter

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates ./templates
EXPOSE 10000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --timeout 300 --workers 1 app:app"]
