# DocSpace for Kubernetes
The following guide covers the installation process of the ‘DocSpace’ into a Kubernetes cluster.

## Requirements

  - Kubernetes version no lower than 1.19+
  - A minimum of three hosts is required for the Kubernetes cluster
  - Resources for the cluster hosts: 4 CPU \ 8 GB RAM min
  - Kubectl is installed on the cluster management host

    Read more on the installation of kubectl [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
  - Helm is installed on the cluster management host
    
    Read more on the installation of Helm [here](https://helm.sh/docs/intro/install/)

## Deploy prerequisites

### 1. Add Helm repositories

```bash
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm repo add stable https://charts.helm.sh/stable
$ helm repo add elastic https://helm.elastic.co
$ helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
$ helm repo update
```

### 2. Install NFS Provisioner

```bash
$ helm install nfs-server stable/nfs-server-provisioner --set persistence.enabled=true,persistence.storageClass=do-block-storage,persistence.size=50Gi
```
See more details about installing NFS Server Provisioner via Helm [here](https://github.com/helm/charts/tree/master/stable/nfs-server-provisioner).

### 3. Install MySQL

#### 3.1 Creating MySQL Secrets

Create a secret containing the `root` user password and the user password to be used by the DocSpace. 
To do this, in the `./sources/secrets/mysql-password.yaml` file, change the values for the `mysql-root-password` and `mysql-password` keys.

Next, create a secret by running the following command:

```bash
$ kubectl apply -f ./sources/secrets/mysql-password.yaml
```

#### 3.2 Installing MySQL:

```bash
$ helm install mysql -f ./sources/mysql_values.yaml bitnami/mysql
```

See more details about installing MySQL via Helm [here](https://github.com/bitnami/charts/tree/master/bitnami/mysql).

### 4 Install the Elasticsearch cluster

```bash
$ helm install elasticsearch --version 7.13.1 -f ./sources/elasticsearch_values.yaml elastic/elasticsearch
```

Test the Elasticsearch cluster by running `helm test elasticsearch`, the output should have the following line:

```bash
Phase:          Succeeded
```

See more details about installing Elasticsearch via Helm [here](https://github.com/elastic/helm-charts/tree/master/elasticsearch).

### 5 Install RabbitMQ

To install RabbitMQ to your cluster, run the following command:

```bash
$ helm install rabbitmq bitnami/rabbitmq \
  --set persistence.size=9Gi \
  --set auth.username=guest \
  --set auth.password=guest \
  --set metrics.enabled=false
```

See more details about installing RabbitMQ via Helm [here](https://github.com/bitnami/charts/tree/master/bitnami/rabbitmq#rabbitmq).

### 6 Install Redis

To install Redis to your cluster, run the following command:

```bash
$ helm install redis bitnami/redis \
  --set architecture=standalone \
  --set auth.enabled=false \
  --set master.persistence.size=9Gi \
  --set metrics.enabled=false
```

See more details about installing Redis via Helm [here](https://github.com/bitnami/charts/tree/master/bitnami/redis).

## Deploy DocSpace

### 1 Install DocSpace

To install DocSpace to your cluster, run the following command:

```bash
$ helm install [RELEASE_NAME] -f values.yaml ./
```

The command deploys DocSpace on the Kubernetes cluster in the default configuration. The [Parameters] section lists the parameters that can be configured during installation.

_See [helm install](https://helm.sh/docs/helm/helm_install/) for command documentation._

### 2 Uninstall DocSpace

To uninstall/delete the `docspace` deployment:

```bash
$ helm uninstall [RELEASE_NAME]
```

The `helm uninstall` command removes all the Kubernetes components associated with the chart and deletes the release.

_See [helm uninstall](https://helm.sh/docs/helm/helm_uninstall/) for command documentation._

### 3 Upgrade DocSpace

It's necessary to set the parameters for updating. For example,

```bash
$ helm upgrade [RELEASE_NAME] ./ \
  --set images.tag=[tag]
```

  > **Note**: also need to specify the parameters that were specified during installation

Or modify the `values.yaml` file and run the command:

  ```bash
  $ helm upgrade [RELEASE_NAME] -f values.yaml ./
  ```

Running the `helm upgrade` command runs a hook that cleans up the directory with libraries and then fills with new ones. This is needed when updating the version of DocSpace. The default hook execution time is 300s.
The execution time can be changed using `--timeout [time]`, for example:

```bash
$ helm upgrade [RELEASE_NAME] -f values.yaml ./ --timeout 15m
```

If you want to update any parameter other than the version of the DocSpace, then run the `helm upgrade` command without `hooks`, for example:

```bash
$ helm upgrade [RELEASE_NAME] ./ --set jwt.enabled=false --no-hooks
```

_See [helm upgrade](https://helm.sh/docs/helm/helm_upgrade/) for command documentation._

To rollback updates, run the following command:

```bash
$ helm rollback [RELEASE_NAME]
```

_See [helm rollback](https://helm.sh/docs/helm/helm_rollback/) for command documentation._

## Parameters

| Parameter           | Description           | Default          |
|---------------------|-----------------------|------------------|

## Configuration and installation details

### 1 Expose DocSpace

#### 1.1 Installing the Kubernetes Nginx Ingress Controller

To install the Nginx Ingress Controller to your cluster, run the following command:

```bash
$ helm install nginx-ingress ingress-nginx/ingress-nginx --set controller.publishService.enabled=true,controller.replicaCount=2
```

See more detail about installing Nginx Ingress Controller via Helm [here](https://github.com/kubernetes/ingress-nginx/tree/master/charts/ingress-nginx).

#### 1.2 Expose DocSpace via HTTP

*You should skip step[2.1.2] if you are going to expose DocSpace via HTTPS*

This type of exposure has more overheads of performance compared with exposure via service, it also creates a loadbalancer to get access to DocSpace.
Use this type if you use external TLS termination and when you have several WEB applications in the k8s cluster. You can use the one set of ingress instances and the one loadbalancer for those. It can optimize the entry point performance and reduce your cluster payments, cause providers can charge a fee for each loadbalancer.

To expose DocSpace via ingress HTTP, set the `ingress.enabled` parameter to true:

```bash
$ helm install docspace ./ --set ingress.enabled=true

```

Run the following command to get the `docspace` ingress IP:

```bash
$ kubectl get ingress ingress-app -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```

After that, DocSpace will be available at `http://DOCSPACE-INGRESS-IP/`.

If the ingress IP is empty, try getting the `docspace` ingress hostname:

```bash
$ kubectl get ingress ingress-app -o jsonpath="{.status.loadBalancer.ingress[*].hostname}"
```

In this case, DocSpace will be available at `http://DOCSPACE-INGRESS-HOSTNAME/`.

#### 1.3 Expose DocSpace via HTTPS

This type of exposure allows you to enable internal TLS termination for DocSpace.

Create the `tls` secret with an ssl certificate inside.

Put the ssl certificate and the private key into the `tls.crt` and `tls.key` files and then run:

```bash
$ kubectl create secret generic tls \
  --from-file=./tls.crt \
  --from-file=./tls.key
```

```bash
$ helm install docspace ./ --set ingress.enabled=true,ingress.tls.enabled=true,ingress.tls.secretName=tls,ingress.host=example.com

```

Run the following command to get the `docspace` ingress IP:

```bash
$ kubectl get ingress ingress-app -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```

If the ingress IP is empty, try getting the `docspace` ingress hostname:

```bash
$ kubectl get ingress ingress-app -o jsonpath="{.status.loadBalancer.ingress[*].hostname}"
```

Associate the `docspace` ingress IP or hostname with your domain name through your DNS provider.

After that, DocSpace will be available at `https://your-domain-name/`.
