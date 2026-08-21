# demo-api

A small FastAPI service for practicing Kubernetes operations and Plural CD.

## Endpoints

- `/`: application version and pod hostname
- `/healthz`: readiness and liveness check
- `/version`: application version
- `/work`: waits for about one second to generate load
- `/uptime`: process uptime

## Build

```sh
docker build -t ghcr.io/pnewell/demo-api:v1 .
docker build -t ghcr.io/pnewell/demo-api:v2 --build-arg APP_VERSION=v2 .
docker push ghcr.io/pnewell/demo-api:v1
docker push ghcr.io/pnewell/demo-api:v2
```

## Deploy

```sh
kubectl apply -f k8s/
kubectl -n demo-api get pods -w
curl http://demo-api.demo-api.svc.cluster.local/version
```

## Pod recovery

Delete one pod and watch the Deployment replace it:

```sh
kubectl -n demo-api get pods
kubectl -n demo-api delete pod <pod-name>
kubectl -n demo-api get pods -w
```

## Rolling upgrade

Change the image tag in `k8s/deployment.yaml` from `v1` to `v2`, then apply it:

```sh
kubectl apply -f k8s/deployment.yaml
kubectl -n demo-api rollout status deployment/demo-api
kubectl -n demo-api get pods -w
```

Use another terminal to send requests during the rollout:

```sh
while true; do
  curl -s http://demo-api.demo-api.svc.cluster.local/version
  echo
  sleep 0.2
done
```

## Autoscaling

Watch the HPA and pods:

```sh
kubectl -n demo-api get hpa -w
kubectl -n demo-api get pods -w
```

Generate load from another terminal:

```sh
while true; do
  curl -s http://demo-api.demo-api.svc.cluster.local/work >/dev/null &
done
```

Stop the load loop with Control-C. The HPA can take several minutes to scale back down.

Use `kubectl top pods -n demo-api` to inspect the CPU values used by the HPA.

## Troubleshooting

### Invalid image

Change the image tag in `k8s/deployment.yaml` to `v999`, then apply it:

```sh
kubectl apply -f k8s/deployment.yaml
kubectl -n demo-api get pods
kubectl -n demo-api describe pod <stuck-pod>
```

The new pod will report `ImagePullBackOff` or `ErrImagePull`. Restore a valid image tag to recover.

### Failed liveness check

Add this environment variable to the container in `k8s/deployment.yaml`:

```yaml
env:
  - name: FAILURE_MODE
    value: "1"
```

Apply the manifest and inspect the pod:

```sh
kubectl apply -f k8s/deployment.yaml
kubectl -n demo-api get pods
kubectl -n demo-api describe pod <pod-name>
kubectl -n demo-api logs <pod-name>
```

Remove the environment variable and apply the manifest again to recover.

## Plural

Plural manages the manifests in `k8s/` from the `main` branch of this repository. The service is deployed to the `local` cluster in the `demo-api` namespace.

After Plural takes ownership, make deployment changes through Git instead of running `kubectl apply`. Commit and push a manifest change, then watch the service sync and roll out in the Plural Console.
