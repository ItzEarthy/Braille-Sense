FROM nginx:alpine
# Use a custom nginx config that proxies /api to the backend service
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html
COPY style.css /usr/share/nginx/html
COPY script.js /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
