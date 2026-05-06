FROM node:20-bookworm-slim
WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		cmake \
		libopencv-dev \
		pkg-config \
		python3 \
		python3-dev \
		python3-venv \
		python3-pip \
		curl \
	&& rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json* ./
RUN npm install --production

COPY . .
COPY requirements.txt ./
# Create an isolated virtual environment to avoid Debian's
# externally-managed environment restrictions (PEP 668).
RUN python3 -m venv /opt/venv \
	&& /opt/venv/bin/pip install --upgrade pip setuptools wheel \
	&& /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Use the virtualenv's python by default for spawned processes
ENV PATH=/opt/venv/bin:$PATH
ENV PYTHON=/opt/venv/bin/python
EXPOSE 5000
CMD ["node", "server.js"]
