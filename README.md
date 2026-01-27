# MiniShaya

## Ejecución de Kubernetes

La carpeta `k8s/` contiene todos los Manifest necesarios para ejecutar el sistema en un cluster de Kubernetes, incluyendo el HPA para los consumidores.

### Dependencias

Es necesario tener instalado lo siguiente:

- Minikube
- kubectl
- helm

### Comandos

Iniciar Minikube

```
minikube start
```

Construir todas las imágenes

```
docker build -t shaya-producer:latest ./producer
docker build -t shaya-consumer:latest ./consumer
docker build -t shaya-notifier:latest ./notifier
```

Cargar las imágenes dentro de Minikube

```
minikube image load shaya-producer:latest
minikube image load shaya-consumer:latest
minikube image load shaya-notifier:latest
```

Habilitar el servidor de métricas, necesario para HPA

```
minikube addons enable metrics-server
```

Aplicar toda la configuración

```
kubectl apply --recursive -f k8s/
```

Agregar el repositorio de Grafana para Helm

```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

Instalar el stack PLG (Promtail+Loki+Grafana)

```
helm upgrade --install loki grafana/loki-stack \
  --namespace=monitoring \
  --create-namespace \
  --set grafana.enabled=true \
  --set promtail.enabled=true \
  --set loki.isDefault=true
```

Una vez el stack está en ejecución, obtener la clave para el dashboard de Grafana

```
kubectl get secret --namespace monitoring loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

Exponer Grafana para acceder desde el navegador

```
kubectl port-forward --namespace monitoring service/loki-grafana 3000:80
```
