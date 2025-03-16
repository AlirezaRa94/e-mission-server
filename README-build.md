# Building and Pushing a Docker Image

## 1️⃣ Building a Docker Image

To build a Docker image, use the following command:

```bash
docker build --platform=linux/amd64 -t my-image .
```

### 🔍 Explanation:

- `docker build` → Command to build a Docker image.
- `--platform=linux/amd64` → Ensures the image is built for `amd64` architecture, useful for compatibility (especially on Apple Silicon Macs which default to `arm64`).
- `-t my-image` → Tags the image with the name `my-image`.
- `.` → Specifies the current directory as the build context (should contain a `Dockerfile`).

## 2️⃣ Pushing the Image to Docker Hub

Once the image is built, push it to Docker Hub:

```bash
docker push my-image
```

### 🔍 Explanation:

- `docker push` → Pushes the image to the Docker registry.
- `my-image` → The name of the image to be pushed.

## 📝 Notes:

- Before pushing, ensure you are logged in to Docker Hub using:
  ```bash
  docker login
  ```
- If pushing to a Docker Hub repository, use the format:
  ```bash
  docker tag my-image my-dockerhub-username/my-image
  docker push my-dockerhub-username/my-image
  ```
- If using a private registry, specify the registry URL:
  ```bash
  docker tag my-image my-registry.com/my-image
  docker push my-registry.com/my-image
  ```

## 🎯 Example Workflow:

```bash
# Login to Docker Hub
docker login

# Build the image for amd64 architecture
docker build --platform=linux/amd64 -t my-dockerhub-username/my-image .

# Push the image to Docker Hub
docker push my-dockerhub-username/my-image
```
