export HUGO_IP_ADDRESS="127.0.0.1"
export HUGO_BASE_URL="http://${HUGO_IP_ADDRESS}:1313"

echo "Starting Hugo dev server on $HUGO_BASE_URL using Docker"
docker run --name hugo_dev_server --rm -it \
    -v "$(pwd)":/src \
    -v "$(pwd)/hugo_cache":/tmp/hugo_cache \
    -p 1313:1313 \
    ghcr.io/hugomods/hugo:base \
    server --bind="0.0.0.0" --baseURL="${HUGO_BASE_URL}" --buildFuture --buildDrafts --poll 1s
