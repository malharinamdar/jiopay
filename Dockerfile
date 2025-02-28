# Use the official Streamlit base image
FROM streamlit/streamlit:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (replaces packages.txt)
RUN apt-get update && \
    apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon-x11-0 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    libxdamage1 \
    libxfixes3 \
    libcairo2 \
    wget \
    xvfb \
    libgtk-3-0 \
    libgbm-dev \
    libnspr4 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxext6 \
    libxslt1.1 \
    libwoff1.0.2-2 \
    libevent-2.1-7 \
    libopus0 \
    libflite1 \
    libflite-usenglish \
    libflite-cmulex \
    libwebpdemux2 \
    libharfbuzz-icu0 \
    libwebpmux3 \
    libenchant-2-2 \
    libsecret-1-0 \
    libhyphen0 \
    libegl1 \
    libgudev-1.0-0 \
    libgles2 \
    libx264-160 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy your application code
COPY . .

# Set the command to run your Streamlit app
CMD ["streamlit", "run", "app.py"]
