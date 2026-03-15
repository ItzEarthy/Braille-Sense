FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --only=production
COPY . .
# install curl so the healthcheck can run inside the container
RUN apk add --no-cache curl
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD curl -f http://localhost:5000/ || exit 1
CMD ["node", "server.js"]
