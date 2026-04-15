FROM nginx:alpine

# Serve static frontend files directly (no Node build required)
COPY index.html /usr/share/nginx/html/
COPY css /usr/share/nginx/html/css/
COPY js /usr/share/nginx/html/js/
COPY setting.png /usr/share/nginx/html/

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
