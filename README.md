# usb

## Local Development

Requirements:

* Kubernetes (we use [microk8s](https://microk8s.io/) in this example)
* [Skaffold](https://skaffold.dev/)


Bootstrap microk8s:

```
microk8s.kubectl config view --raw > $HOME/.kube/config
microk8s.enable registry ingress dns
```

Start services with Skaffold:

```
skaffold dev --default-repo=localhost:32000
```

Visit the services:

* Appsearch: http://appsearch-127-0-0-1.nip.io/
