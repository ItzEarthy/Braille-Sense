FROM node:20 as builder
WORKDIR /app

# Use a custom nginx config that proxies /api to the backend service

COPY . .
run npm install

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chmod -R 755 /usr/share/nginx/html


EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
