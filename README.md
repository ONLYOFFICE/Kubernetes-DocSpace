# AppServer for Kubernetes
The following guide covers the installation process of the ‘AppServer’ into a Kubernetes cluster.

## Requirements
  - Kubernetes version no lower than 1.19+
  - A minimum of three hosts is required for the Kubernetes cluster
  - Resources for the cluster hosts: 4 CPU \ 8 GB RAM min
  - Kubectl is installed on the cluster management host

    Read more on the installation of kubectl [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
  - Helm is installed on the cluster management host
    
    Read more on the installation of Helm [here](https://helm.sh/docs/intro/install/)

## 1. Add Helm repositories
```
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm repo add stable https://charts.helm.sh/stable
$ helm repo add elastic https://helm.elastic.co
$ helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
$ helm repo update
```

## 2. Installing NFS Provisioner
```
$ helm install nfs-server stable/nfs-server-provisioner --set persistence.enabled=true,persistence.storageClass=do-block-storage,persistence.size=50Gi
```
Read more on the installation of NFS Server Provisioner [here](https://github.com/helm/charts/tree/master/stable/nfs-server-provisioner)

## 3. Installing the AppServer components

### 3.1 Creating storages
Open the repo directory and run the command:
```
$ kubectl apply -f ./pvc/pvc.yaml
```

### 3.2 Creating Kubernetes Secrets
In the Secret named `mysql-password`, edit the `stringData.mysql-root-password` field by entering your password instead of `my-secret-pw`;
edit the `stringData.mysql-password` field by entering your password instead of `onlyoffice_pass`.

In the Secret named `appserver-all`, change to your own variable values in fields `stringData.APP_CORE_MACHINEKEY`, `stringData.JWT_SECRET`, `stringData.JWT_HEADER`.

*Note: By default, AppServer services are installed in `namespace`: `default`.
If a different `namespace` is used for the installation, change the value for all variables containing `default` to your own.
(For example, for `namespace` `onlyoffice` you can run the command: `sed -i 's/default/onlyoffice/' ./secret/secret.yaml`).*
```
$ kubectl apply -f ./secret/secret.yaml
```

### 3.3 Installing MySQL
Install the MySQL configmap:
```
$ kubectl create configmap mysql-init \
  --from-file=./mysql/01_createdb.sql \
  --from-file=./mysql/02_onlyoffice.sql \
  --from-file=./mysql/03_onlyoffice.data.sql \
  --from-file=./mysql/04_onlyoffice.upgradev110.sql \
  --from-file=./mysql/05_onlyoffice.upgradev111.sql \
  --from-file=./mysql/06_onlyoffice.upgradev115.sql
```
Install MySQL:
```
$ helm install mysql -f ./mysql/mysql_values.yaml bitnami/mysql
```

Check the pod readiness by running the following command:
```
$ kubectl logs -f $(kubectl get pod -o wide | grep mysql | awk '{print $1}') | grep -i 'ready for connections'
```
Wait in the output for the lines containing `ready for connections` and press `CTRL+C`

Read more on the installation of MySQL [here](https://github.com/bitnami/charts/tree/master/bitnami/mysql)

### 3.4 Installing the Elasticsearch cluster
```
$ helm install elasticsearch --version 7.9.3 -f ./elasticsearch/elasticsearch_values.yaml elastic/elasticsearch
```
Check the readiness of the Elasticsearch pods by running the following command:
```
$ kubectl get pod -o wide | grep -i elasticsearch
```
The output should have three pods with the running status:
```
NAME                                           READY   STATUS    
elasticsearch-master-0                         1/1     Running   
elasticsearch-master-1                         1/1     Running   
elasticsearch-master-2                         1/1     Running   
```
Test the cluster by running `helm test elasticsearch`, the output should have the following line
```
Phase:          Succeeded
```
Delete the test pod by running `kubectl delete pod elasticsearch-xxxxx-xxxx`, where ‘elasticsearch-xxxxx-xxxx’ is the name of the test pod

Read more on the installation of Elasticsearch [here](https://github.com/elastic/helm-charts/tree/master/elasticsearch)

### 3.5 Installing Zookeeper
```
$ helm install onlyoffice-zookeeper -f ./zookeeper/zookeeper_values.yaml bitnami/zookeeper
```
Read more on the installation of Zookeeper [here](https://github.com/bitnami/charts/tree/master/bitnami/zookeeper)

### 3.6 Installing Kafka
```
$ helm install onlyoffice-kafka -f ./kafka/kafka_values.yaml bitnami/kafka
```
Read more on the installation of Kafka [here](https://github.com/bitnami/charts/tree/master/bitnami/kafka)

### 3.7 Installing AppServer
```
$ kubectl apply -f ./app/
```

## 4. Providing access to the ONLYOFFICE portal

### 4.1 Installing dependencies
```
$ helm install nginx-ingress ingress-nginx/ingress-nginx --set controller.publishService.enabled=true
```
Read more on the installation of NGINX Ingress Controller [here](https://github.com/kubernetes/ingress-nginx/tree/master/charts/ingress-nginx)

### 4.2 Access using HTTP
```
kubectl apply -f ./ingress/app-ingress.yaml
```
Run the following command to get the ingress IP:
```
$ kubectl get ingresses.v1.networking.k8s.io ingress-appserver -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```
The portal will be available over HTTP at `http://INGRESS-IP/`.
