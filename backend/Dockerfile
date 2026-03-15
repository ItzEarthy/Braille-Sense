FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --only=production
COPY . .
RUN apk add --no-cache curl
EXPOSE 5000
CMD ["node", "server.js"]
