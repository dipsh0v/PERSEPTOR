#!/bin/sh
set -e

# Set default values if not provided
export NGINX_PORT=${NGINX_PORT:-3000}
export BACKEND_SERVICE=${BACKEND_SERVICE:-backend}
export BACKEND_PORT=${BACKEND_PORT:-5000}

# Substitute environment variables in nginx config template
envsubst '${NGINX_PORT} ${BACKEND_SERVICE} ${BACKEND_PORT}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

# Print config for debugging
echo "Generated nginx configuration:"
cat /etc/nginx/conf.d/default.conf

# Start nginx
exec nginx -g "daemon off;"

