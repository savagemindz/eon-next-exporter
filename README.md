# eon-next

The eon next api only exports monthly billing metrics at this time so this utility is not particularly useful. This attempts to work around this by setting a custom timestamp on the metrics. Anyway this repo is untested.

# eon-next-exporter

Eon Next Meter reading Prometheus exporter.

This program can scrape data from Eon-Next Kraken API and format it such that Prometheus can scrape it.

I designed this to run on my home kubernetes cluster but it could just as easily be run using docker.

## Install
### Kubernetes
```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eon-next-exporter
  namespace: monitoring
  labels:
    app: eon-next-exporter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: eon-next-exporter
  template:
    metadata:
      labels:
        app: eon-next-exporter
    spec:
      nodeSelector:
        kubernetes.io/arch: amd64
      containers:
        - name: eon-next-exporter
          image: savagemindz/eon-next-exporter:latest
          resources:
            requests:
              cpu: 100m
              memory: "64M"
            limits:
              cpu: 100m
              memory: "128M"
          ports:
            - containerPort: 9101
              protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: eon-next-exporter-service
  namespace: monitoring
spec:
  selector:
    app: eon-next-exporter
  ports:
    - name: http
      protocol: TCP
      port: 9101
      targetPort: 9101
```

### Docker
```
docker run -d -p 9101:9101 savagemindz/eon-next-exporter
```
```yaml
# scrape tplink devices
scrape_configs:
  - job_name: 'eon-next-exporter'
    static_configs:
      - targets:
        # IP of the exporter
        - eon-next-exporter-service:9101
    params:
      username:
        - "my@eon_email_address"
      password:
        - "my_eon_password"
```

## Docker Build Instructions
```
docker build -t eon-next-exporter ./
```

## Forked from:

- https://github.com/madmachinations/eon-next
- https://github.com/savagemindz/tplink-powerstats