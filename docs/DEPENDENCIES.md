# Deploying Dependencies

It is assumed that all dependencies will be deployed in a clustered HA mode and that 3 worker nodes with 4 CPU and 8 GiB RAM each will be allocated for them, with the taint `For=dep:NoSchedule` and the label `For=dep` added. If you change these, update the corresponding fields in the manifests below.

Change the number/resources of the worker nodes and the parameter values if necessary.

## Deploy MySQL Database

[MySQL Operator for Kubernetes](https://dev.mysql.com/doc/mysql-operator/en/)

Install the MySQL Operator:

```bash
helm repo add mysql-operator https://mysql.github.io/mysql-operator/
helm repo update

helm install mysql-operator --version 2.3.1 mysql-operator/mysql-operator \
  --namespace mysql-operator \
  --create-namespace \
  --set envs.k8sClusterDomain=cluster.local
```

For more details, see [here](https://github.com/mysql/mysql-operator).

Create a `mysql.yaml` manifest with the following content:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-root
type: Opaque
stringData:
  rootUser: root
  rootHost: "%"
  rootPassword: "password"

---
apiVersion: v1
kind: Secret
metadata:
  name: mysql
type: Opaque
stringData:
  mysql-password: "password"

---
apiVersion: batch/v1
kind: Job
metadata:
  name: mysql-db-provisioning
spec:
  backoffLimit: 6
  ttlSecondsAfterFinished: 300
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: provisioning
        image: onlyoffice/docs-utils:9.4.1-1
        env:
        - name: DB_HOST
          value: mysql
        - name: DB_PORT
          value: "3306"
        - name: DB_NAME
          value: docspace
        - name: DB_USER
          value: onlyoffice_user
        - name: ADMIN_USER
          valueFrom:
            secretKeyRef:
              name: mysql-root
              key: rootUser
        - name: ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-root
              key: rootPassword
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql
              key: mysql-password
        command: ["/bin/sh", "-c"]
        args:
        - |
          set -e
          until mysql -h"$DB_HOST" -P"$DB_PORT" -u"$ADMIN_USER" -p"$ADMIN_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
            echo "waiting for MySQL at $DB_HOST:$DB_PORT"
            sleep 5
          done
          mysql -h"$DB_HOST" -P"$DB_PORT" -u"$ADMIN_USER" -p"$ADMIN_PASSWORD" <<EOSQL
          CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci;
          CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
          ALTER USER '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
          GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'%';
          FLUSH PRIVILEGES;
          EOSQL
          echo "database $DB_NAME and user $DB_USER are ready"
```

> **Note:**\
> In the `mysql-root` and `mysql` secrets, specify your own passwords.

> **Note:**\
> Unlike the bitnami chart, the operator does not create the database and the user. This is done by the `mysql-db-provisioning` job, it waits until the cluster is available.

Apply the created manifest:

```bash
kubectl apply -f mysql.yaml
```

Create a `mysql_values.yaml` file with the following content:

```yaml
serverVersion: 8.4.8

serverInstances: 3
routerInstances: 2

credentials:
  root:
    secretName: mysql-root

tls:
  useSelfSigned: true

datadirVolumeClaimTemplate:
  storageClassName: PERSISTENT_STORAGE_CLASS
  accessModes: ReadWriteOnce
  resources:
    requests:
      storage: 40Gi

serverConfig:
  mycnf: |
    [mysqld]
    sql_mode=NO_ENGINE_SUBSTITUTION
    max_connections=1000
    max_allowed_packet=1048576000
    group_concat_max_len=2048
    character_set_server=utf8mb3
    collation_server=utf8mb3_general_ci
    skip_name_resolve=ON
    explicit_defaults_for_timestamp=ON
    loose_group_replication_transaction_size_limit=1073741824

podSpec:
  nodeSelector:
    For: dep
  tolerations:
  - key: "For"
    operator: "Equal"
    value: "dep"
    effect: "NoSchedule"
  containers:
  - name: mysql
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi
      limits:
        cpu: 4000m
        memory: 4Gi
```

> **Note:**\
> `serverVersion` is set to `8.4.8`, the 8.4 LTS branch. Without it, the operator installs its own default version, which has not been tested with DocSpace.

> **Note:**\
> Group Replication requires a primary key on every table. Use a DocSpace version in which the `identity_client_*` tables have primary keys, otherwise the migrations fail.

Install the InnoDB Cluster:

```bash
helm install mysql --version 2.3.1 mysql-operator/mysql-innodbcluster -f mysql_values.yaml
```

This creates one primary and two secondaries in Group Replication, and MySQL Router available via the `mysql` service.

> **Note:**\
> If you set `serverInstances: 1`, only the primary will be created.

To install DocSpace, specify the corresponding parameters:

```yaml
docs:
  connections:
    dbType: mysql
    dbHost: mysql
    dbUser: onlyoffice_user
    dbPort: "3306"
    dbName: docspace
    dbExistingSecret: mysql
    dbSecretKeyName: mysql-password

connections:
  mysqlHost: mysql
  mysqlPort: "3306"
  mysqlDatabase: docspace
  mysqlUser: onlyoffice_user
  mysqlExistingSecret: mysql
  mysqlSecretKeyPassword: mysql-password
```

## Deploy RabbitMQ

[RabbitMQ Cluster Operator](https://www.rabbitmq.com/kubernetes/operator/operator-overview)

> **Note:**\
> Cluster Operator 2.20+ requires cert-manager to be installed. If cert-manager is not present in the cluster and installing it is undesirable, use Cluster Operator ≤ 2.19.

Install [cert-manager](https://cert-manager.io/docs/usage/gateway/). You can follow [this step](./GATEWAY.md#expose-onlyoffice-docspace-via-https-using-the-lets-encrypt-certificate) of the instructions.

Install the RabbitMQ Cluster Operator:

```bash
kubectl apply -f https://github.com/rabbitmq/cluster-operator/releases/download/v2.22.3/cluster-operator.yml
```

For more details, see [here](https://github.com/rabbitmq/cluster-operator).

Create a `rabbitmq.yaml` manifest with the following content:

```yaml
apiVersion: rabbitmq.com/v1beta1
kind: RabbitmqCluster
metadata:
  name: rabbitmq
spec:
  replicas: 3
  persistence:
    storageClassName: PERSISTENT_STORAGE_CLASS
    storage: 10Gi
  rabbitmq:
    additionalConfig: |
      default_user = onlyoffice
      cluster_partition_handling = autoheal
      queue_leader_locator = balanced
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
  tolerations:
    - key: "For"
      operator: "Equal"
      value: "dep"
      effect: "NoSchedule"
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: For
                operator: In
                values:
                  - dep
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app.kubernetes.io/name
              operator: In
              values:
              - rabbitmq
          topologyKey: kubernetes.io/hostname
        weight: 100
```

> **Note:**\
> `spec.persistence.storage` must not be less than `disk_free_limit.absolute` (2GB by default) to avoid triggering a disk alarm, which would block the publisher.

> **Note:**\
> The metrics exporter is enabled by default. The Cluster Operator deploys
> RabbitMQ with the `rabbitmq_prometheus` plugin activated, exposing Prometheus
> metrics on port `15692` (`/metrics`).

Apply the created manifest:

```bash
kubectl apply -f rabbitmq.yaml
```

To install DocSpace, specify the corresponding parameters:

```yaml
docs:
  connections:
    amqpType: rabbitmq
    amqpHost: rabbitmq
    amqpPort: "5672"
    amqpVhost: "/"
    amqpUser: onlyoffice
    amqpProto: amqp
    amqpExistingSecret: rabbitmq-default-user
    amqpSecretKeyName: password

connections:
  brokerHost: rabbitmq
  brokerPort: "5672"
  brokerVhost: "/"
  brokerUser: onlyoffice
  brokerProto: amqp
  brokerExistingSecret: rabbitmq-default-user
  brokerSecretKeyName: password
```

## Deploy Valkey

[Valkey Cluster Operator](https://github.com/valkey-io/valkey-operator)

Install the Valkey Cluster Operator:

```bash
helm repo add valkey https://valkey.io/valkey-helm/
helm repo update

helm install valkey --version 0.5.0 valkey/valkey-operator \
  --namespace valkey-operator-system \
  --create-namespace
```

For more details, see [here](https://github.com/valkey-io/valkey-helm/tree/main/valkey-operator).

Create a `valkey.yaml` manifest with the following content:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: docs-valkey-cluster
type: Opaque
stringData:
  valkey-password: "password"

---
apiVersion: valkey.io/v1alpha1
kind: ValkeyCluster
metadata:
  name: valkey
spec:
  shards: 1
  replicas: 0
  persistence:
    size: 10Gi
    storageClassName: PERSISTENT_STORAGE_CLASS
  users:
    - name: default
      passwordSecret:
        name: docs-valkey-cluster
        keys: [valkey-password]
      permissions: "+@all ~* &*"
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
  scheduling:
    nodeSelector:
      For: dep
    tolerations:
      - key: "For"
        operator: "Equal"
        value: "dep"
        effect: "NoSchedule"
  exporter:
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 2000m
        memory: 2Gi
```

> **Note:**\
> In the `docs-valkey-cluster` secret, specify your own password for the `valkey-password` key.

> **Note:**\
> DocSpace requires Valkey with a single node: `spec.shards: 1` and `spec.replicas: 0`.

> **Note:**\
> The metrics exporter is enabled by default. Each pod runs a `metrics-exporter`
> sidecar exposing Prometheus metrics on port `9121` (`/metrics`). To disable it, set
> `spec.exporter.enabled: false` in the `ValkeyCluster` manifest.

Apply the created manifest:

```bash
kubectl apply -f valkey.yaml
```

To install DocSpace, specify the corresponding parameters:

```yaml
docs:
  connections:
    redisConnectorName: redis
    redisUser: default
    ## Only DB 0 is used in the cluster version
    redisDBNum: "0"
    redisClusterNodes:
    - valkey-valkey:6379
    redisExistingSecret: docs-valkey-cluster
    redisSecretKeyName: valkey-password
    redisNoPass: false

connections:
  redisHost: valkey-valkey.default.svc.cluster.local
  redisPort: "6379"
  redisUser: default
  ## Only DB 0 is used in the cluster version
  redisDB: "0"
  redisExistingSecret: docs-valkey-cluster
  redisSecretKeyName: valkey-password
  redisNoPass: false
```
