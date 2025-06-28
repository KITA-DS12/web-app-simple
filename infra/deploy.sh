#!/bin/bash

# Usage: ./deploy.sh IMAGE_NAME SERVICE_NAME REGION
# Example: ./deploy.sh gcr.io/my-project/app my-app us-central1

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 IMAGE_NAME SERVICE_NAME REGION"
    exit 1
fi

IMAGE=$1
SERVICE=$2
REGION=$3

echo "Building and pushing image: $IMAGE"
gcloud builds submit --tag "$IMAGE" .

if [ $? -ne 0 ]; then
    echo "Build failed"
    exit 1
fi

echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE" \
    --image "$IMAGE" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}"

if [ $? -eq 0 ]; then
    echo "Deployment successful!"
else
    echo "Deployment failed"
    exit 1
fi