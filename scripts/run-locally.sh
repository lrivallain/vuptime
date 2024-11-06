export HUGO_IP_ADDRESS="$(hostname -I | tr -d ' ')"
export HUGO_BASE_URL="http://${HUGO_IP_ADDRESS}:1313"

echo "Starting Hugo dev server on $HUGO_BASE_URL"
hugo server \
    --bind="${HUGO_IP_ADDRESS}" \
    --baseURL="${HUGO_BASE_URL}" \
    --buildFuture --buildDrafts #\
    #--poll 1s \ # Use pooling to force file change detection in a WSL environment
