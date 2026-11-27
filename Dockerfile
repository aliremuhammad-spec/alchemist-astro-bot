FROM python:3.13-slim

# librsvg: SVG -> PNG for charts sent in chat. Noto fonts: Arabic shaping + astrology glyphs.
# Pango/HarfBuzz: WeasyPrint for the PDF report.
RUN apt-get update && apt-get install -y --no-install-recommends \
      librsvg2-bin fonts-noto-core fonts-dejavu-core tzdata \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libharfbuzz-subset0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts ./scripts
RUN python scripts/build_cities.py data/geo

COPY app ./app
COPY web ./web
COPY docs ./docs
COPY content ./content

ENV PYTHONUNBUFFERED=1 PORT=10000
EXPOSE 10000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
