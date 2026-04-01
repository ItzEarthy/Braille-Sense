FROM node:18-bullseye-slim
WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		cmake \
		libopencv-dev \
		pkg-config \
		python3-dev \
		curl \
	&& rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json* ./
RUN npm install --production

COPY . .
EXPOSE 5000
CMD ["node", "server.js"]
