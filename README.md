# DocSpace for Kubernetes
The following guide covers the installation process of the ‘DocSpace’ into a Kubernetes cluster or OpenShift cluster.

## Contents
- [Requirements](#requirements)
- [Deploy prerequisites](#deploy-prerequisites)
  * [1. Add Helm repositories](#1-add-helm-repositories)
  * [2. Install NFS Provisioner](#2-install-nfs-provisioner)
  * [3. Install MySQL](#3-install-mysql)
  * [4. Install RabbitMQ](#4-install-rabbitmq)
  * [5. Install Redis](#5-install-redis)
  * [6. Install Elasticsearch](#6-install-opensearch)
  * [7. Make changes to the configuration files (optional)](#7-make-changes-to-the-configuration-files-optional)
    + [7.1 Create a Secret containing a json file](#71-create-a-secret-containing-a-json-file)
    + [7.2 Specify parameters when installing DocSpace](#72-specify-parameters-when-installing-docspace)
- [Deploy DocSpace](#deploy-docspace)
  * [1. Install DocSpace](#1-install-docspace)
  * [2. Uninstall DocSpace](#2-uninstall-docspace)
  * [3. Upgrade DocSpace](#3-upgrade-docspace)
- [Parameters](#parameters)
  * [Common parameters](#common-parameters)
  * [DocSpace Application parameters](#docspace-application-parameters)
  * [DocSpace Router Application additional parameters](#docspace-router-application-additional-parameters)
  * [DocSpace Api System Application additional parameters](#docspace-api-system-application-additional-parameters)
  * [DocSpace Doceditor Application additional parameters](#docspace-doceditor-application-additional-parameters)
  * [DocSpace Login Application additional parameters](#docspace-login-application-additional-parameters)
  * [DocSpace Socket Application additional parameters](#docspace-socket-application-additional-parameters)
  * [DocSpace Ssoauth Application additional parameters](#docspace-ssoauth-application-additional-parameters)
  * [DocSpace Proxy Frontend Application additional parameters](#docspace-proxy-frontend-application-additional-parameters)
  * [DocSpace Document Server StatefulSet additional parameters](#docspace-document-server-statefulset-additional-parameters)
  * [DocSpace Ingress parameters](#docspace-ingress-parameters)
  * [DocSpace Jobs parameters](#docspace-jobs-parameters)
  * [DocSpace Elasticsearch parameters](#docspace-opensearch-parameters)
  * [DocSpace Test parameters](#docspace-test-parameters)
- [Configuration and installation details](#configuration-and-installation-details)
  * [1. Expose DocSpace](#1-expose-docspace)
    + [1.1 Expose DocSpace via Service (HTTP Only)](#11-expose-docspace-via-service-http-only)
    + [1.2 Expose DocSpace via Ingress](#12-expose-docspace-via-ingress)
    + [1.2.1 Installing the Kubernetes Nginx Ingress Controller](#121-installing-the-kubernetes-nginx-ingress-controller)
    + [1.2.2 Expose DocSpace via HTTP](#122-expose-docspace-via-http)
    + [1.2.3 Expose DocSpace via HTTPS](#123-expose-docspace-via-https)
  * [2. Transition from ElasticSearch to OpenSearch](#2-transition-from-elasticsearch-to-opensearch)
- [DocSpace installation test (optional)](#docspace-installation-test-optional)

## Requirements

  - Kubernetes version no lower than 1.19+ or OpenShift version no lower than 3.11+
  - A minimum of two hosts is required for the Kubernetes cluster
  - Resources for the cluster hosts: 4 CPU \ 8 GB RAM min
  - Kubectl is installed on the cluster management host. Read more on the installation of kubectl [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
  - Helm v3.7+ is installed on the cluster management host. Read more on the installation of Helm [here](https://helm.sh/docs/intro/install/)
  - If you use OpenShift, you can use both `oc` and `kubectl` to manage deploy.
  - If the installation of components external to ‘DocSpace’ is performed from Helm Chart in an OpenShift cluster, then it is recommended to install them from a user who has the `cluster-admin` role, in order to avoid possible problems with access rights. See [this](https://docs.openshift.com/container-platform/4.7/authentication/using-rbac.html) guide to add the necessary roles to the user.

## Deploy prerequisites

Note: It may be required to apply `SecurityContextConstraints` policy when installing into OpenShift cluster, which adds permission to run containers from a user whose `ID = 1000` and `ID = 1001`.

To do this, run the following commands:

```
$ oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-DocSpace/main/sources/scc/helm-components.yaml
$ oc adm policy add-scc-to-group scc-helm-components system:authenticated
```

### 1. Add Helm repositories

```bash
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm repo add nfs-server-provisioner https://kubernetes-sigs.github.io/nfs-ganesha-server-and-external-provisioner
$ helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
$ helm repo add onlyoffice https://download.onlyoffice.com/charts/stable
$ helm repo update
```

### 2. Install NFS Provisioner

Note: When installing NFS Server Provisioner, Storage Classes - `NFS` is created. When installing to an OpenShift cluster, the user must have a role that allows you to create Storage Classes in the cluster. Read more [here](https://docs.openshift.com/container-platform/4.7/storage/dynamic-provisioning.html).

```bash
$ helm install nfs-server nfs-server-provisioner/nfs-server-provisioner \
  --set persistence.enabled=true \
  --set "storageClass.mountOptions={vers=4,timeo=20}" \
  --set persistence.storageClass=PERSISTENT_STORAGE_CLASS \
  --set persistence.size=PERSISTENT_SIZE
```

- `PERSISTENT_STORAGE_CLASS` is a Persistent Storage Class available in your Kubernetes cluster.

- `PERSISTENT_SIZE` is the total size of all Persistent Storages for the nfs Persistent Storage Class. Must be at least the sum of the values of the `persistence` and `opensearch.persistence.size` parameters if `persistence.storageClass=nfs` and `opensearch.persistence.storageClass=nfs`. You can express the size as a plain integer with one of these suffixes: `T`, `G`, `M`, `Ti`, `Gi`, `Mi`. For example: `19Gi`.

See more details about installing NFS Server Provisioner via Helm [here](https://github.com/kubernetes-sigs/nfs-ganesha-server-and-external-provisioner/tree/master/charts/nfs-server-provisioner).

*The PersistentVolume type to be used for PVC placement must support Access Mode [ReadWriteMany](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes).*

*Also, PersistentVolume must have as the owner the user from whom the DocSpace will be started. By default it is `onlyoffice` (104:107).*

### 3. Install MySQL

To install MySQL to your cluster, run the following command:

```bash
$ helm install mysql -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-DocSpace/main/sources/mysql_values.yaml bitnami/mysql \
  --set auth.database=docspace \
  --set auth.username=onlyoffice_user \
  --set primary.persistence.storageClass=PERSISTENT_STORAGE_CLASS \
  --set primary.persistence.size=PERSISTENT_SIZE \
  --set metrics.enabled=false
```

See more details about installing MySQL via Helm [here](https://github.com/bitnami/charts/tree/main/bitnami/mysql).

Here `PERSISTENT_SIZE` is a size for the Database persistent volume. For example: `8Gi`.

### 4. Install RabbitMQ

To install RabbitMQ to your cluster, run the following command:

```bash
$ helm install rabbitmq bitnami/rabbitmq \
  --set persistence.storageClass=PERSISTENT_STORAGE_CLASS \
  --set metrics.enabled=false
```

See more details about installing RabbitMQ via Helm [here](https://github.com/bitnami/charts/tree/main/bitnami/rabbitmq#rabbitmq).

### 5. Install Redis

To install Redis to your cluster, run the following command:

```bash
$ helm install redis bitnami/redis \
  --set architecture=standalone \
  --set master.persistence.storageClass=PERSISTENT_STORAGE_CLASS \
  --set metrics.enabled=false
```

See more details about installing Redis via Helm [here](https://github.com/bitnami/charts/tree/main/bitnami/redis).

### 6. Install Opensearch

To install Opensearch to your cluster, set the `opensearch.enabled=true` parameter when installing DocSpace

### 7. Make changes to the configuration files (optional)

#### 7.1 Create a Secret containing a json file

To create a Secret containing configuration files for overriding default values and additional configuration files for DocSpace, you need to run the following command:

```bash
$ kubectl create secret generic docspace-custom-config \
  --from-file=./appsettings.test.json \
  --from-file=./notify.test.json
```

Note: Any name can be used instead of `docspace-custom-config`.

Note: The example above shows two configuration files. You can use as many as you want, as well as only one file.

Note: When using the `test` suffix in the file name, set the `connections.envExtension` parameter to `test`.

#### 7.2 Specify parameters when installing DocSpace

When installing DocSpace, specify the `extraConf.secretName=docspace-custom-config` and `extraConf.filename={appsettings.test.json,notify.test.json}` parameters.

Note: If you need to add a configuration file after the DocSpace is already installed, you need to execute step [7.1](#71-create-a-secret-containing-a-json-file)
and then run the `helm upgrade [RELEASE_NAME] onlyoffice/docspace --set extraConf.secretName=docspace-custom-config --set "extraConf.filename={appsettings.test.json,notify.test.json}" --no-hooks` command or
`helm upgrade [RELEASE_NAME] -f ./values.yaml onlyoffice/docspace --no-hooks` if the parameters are specified in the `values.yaml` file.

## Deploy DocSpace

Note: It may be required to apply `SecurityContextConstraints` policy when installing into OpenShift cluster, which adds permission to run containers from a user whose `ID = 104`.

To do this, run the following commands:

```
$ oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-DocSpace/main/sources/scc/docspace-components.yaml
$ oc adm policy add-scc-to-group scc-docspace-components system:authenticated
```

Also, you must set the `podSecurityContext.enabled` parameter to `true`:

```
$ helm install [RELEASE_NAME] onlyoffice/docspace --set podSecurityContext=true
```

### 1. Install DocSpace

To install DocSpace to your cluster, run the following command:

```bash
$ helm install [RELEASE_NAME] -f values.yaml onlyoffice/docspace
```

The command deploys DocSpace on the Kubernetes cluster in the default configuration. The [Parameters] section lists the parameters that can be configured during installation.

_See [helm install](https://helm.sh/docs/helm/helm_install/) for command documentation._

### 2. Uninstall DocSpace

To uninstall/delete the `docspace` deployment:

```bash
$ helm uninstall [RELEASE_NAME]
```

The `helm uninstall` command removes all the Kubernetes components associated with the chart and deletes the release.

_See [helm uninstall](https://helm.sh/docs/helm/helm_uninstall/) for command documentation._

### 3. Upgrade DocSpace

Note: If you have Elasticsearch installed, please read [this section](#2-transition-from-elasticsearch-to-opensearch).

It's necessary to set the parameters for updating. For example,

```bash
$ helm upgrade [RELEASE_NAME] onlyoffice/docspace \
  --set images.tag=[tag]
```

  > **Note**: also need to specify the parameters that were specified during installation

Or modify the `values.yaml` file and run the command:

  ```bash
  $ helm upgrade [RELEASE_NAME] -f values.yaml onlyoffice/docspace
  ```

Running the `helm upgrade` command runs a hook that cleans up the directory with libraries and then fills with new ones. This is needed when updating the version of DocSpace. The default hook execution time is 300s.
The execution time can be changed using `--timeout [time]`, for example:

```bash
$ helm upgrade [RELEASE_NAME] -f values.yaml onlyoffice/docspace --timeout 15m
```

If you want to update any parameter other than the version of the DocSpace, then run the `helm upgrade` command without `hooks`, for example:

```bash
$ helm upgrade [RELEASE_NAME] onlyoffice/docspace --set jwt.enabled=false --no-hooks
```

_See [helm upgrade](https://helm.sh/docs/helm/helm_upgrade/) for command documentation._

To rollback updates, run the following command:

```bash
$ helm rollback [RELEASE_NAME]
```

_See [helm rollback](https://helm.sh/docs/helm/helm_rollback/) for command documentation._

## Parameters

### Common parameters

| Parameter                                              | Description                                                                                                                 | Default                       |
|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| `connections.envExtension`                             | Defines whether an environment will be used                                                                                 | `none`                        |
| `connections.installationType`                         | Defines solution type                                                                                                       | `ENTERPRISE`                  |
| `connections.migrationType`                            | Defines migration type                                                                                                      | `STANDALONE`                  |
| `connections.mysqlDatabaseMigration`                   | Enables database migration                                                                                                  | `false`                       |
| `connections.mysqlHost`                                | The IP address or the name of the Database host                                                                             | `mysql`                       |
| `connections.mysqlPort`                                | Database server port number                                                                                                 | `3306`                        |
| `connections.mysqlDatabase`                            | Name of the Database the application will be connected with. The database must already exist                                | `docspace`                    |
| `connections.mysqlUser`                                | Database user                                                                                                               | `onlyoffice_user`             |
| `connections.mysqlPassword`                            | Database user password. If set to, it takes priority over the `connections.mysqlExistingSecret`                             | `""`                          |
| `connections.mysqlExistingSecret`                      | Name of existing secret to use for Database passwords. Must contain the key specified in `connections.mysqlSecretKeyPassword` | `mysql`                     |
| `connections.mysqlSecretKeyPassword`                   | The name of the key that contains the Database user password. If you set a password in `connections.mysqlPassword`, a secret will be automatically created, the key name of which will be the value set here | `mysql-password` |
| `connections.redisHost`                                | The IP address or the name of the Redis host. If Redis is deployed inside a k8s cluster, then you need to specify the [FQDN](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#services) name of the service | `redis-master.default.svc.cluster.local` |
| `connections.redisPort`                                | The Redis server port number                                                                                                | `6379`                        |
| `connections.redisUser`                                | The Redis [user](https://redis.io/docs/management/security/acl/) name                                                       | `default`                     |
| `connections.redisExistingSecret`                      | Name of existing secret to use for Redis password. Must contain the key specified in `connections.redisSecretKeyName`       | `redis`                       |
| `connections.redisSecretKeyName`                       | The name of the key that contains the Redis user password. If you set a password in `connections.redisPassword`, a secret will be automatically created, the key name of which will be the value set here | `redis-password` |
| `connections.redisPassword`                            | The password set for the Redis account. If set to, it takes priority over the `connections.redisExistingSecret`             | `""`                          |
| `connections.redisNoPass`                              | Defines whether to use a Redis auth without a password. If the connection to Redis server does not require a password, set the value to `true` | `false`    |
| `connections.brokerHost`                               | The IP address or the name of the Broker host                                                                               | `rabbitmq`                    |
| `connections.brokerPort`                               | The port for the connection to Broker host                                                                                  | `5672`                        |
| `connections.brokerVhost`                              | The virtual host for the connection to Broker host                                                                          | `/`                           |
| `connections.brokerUser`                               | The username for the Broker account                                                                                         | `guest`                       |
| `connections.brokerProto`                              | The protocol for the connection to Broker host                                                                              | `amqp`                        |
| `connections.brokerUri`                                | A string containing the necessary connection parameters to Broker. If set to, it takes priority                             | `""`                          |
| `connections.brokerExistingSecret`                     | The name of existing secret to use for Broker password. Must contain the key specified in `connections.brokerSecretKeyName` | `rabbitmq`                    |
| `connections.brokerSecretKeyName`                      | The name of the key that contains the Broker user password. If you set a password in `connections.brokerPassword`, a secret will be automatically created, the key name of which will be the value set here | `rabbitmq-password` |
| `connections.brokerPassword`                           | Broker user password. If set to, it takes priority over the `connections.brokerExistingSecret`                              | `""`                          |
| `connections.elkSheme`                                 | The protocol for the connection to Opensearch                                                                            | `http`                        |
| `connections.elkHost`                                  | The IP address or the name of the Opensearch host                                                                        | `opensearch`               |
| `connections.elkPort`                                  | The port for the connection to Opensearch                                                                                | `9200`                        |
| `connections.elkThreads`                               | Number of threads in Opensearch                                                                                          | `1`                           |
| `connections.apiHost`                                  | The name of the DocSpace Api service                                                                                        | `api`                         |
| `connections.apiSystemHost`                            | The name of the DocSpace Api System service                                                                                 | `api-system`                  |
| `connections.notifyHost`                               | The name of the DocSpace Notify service                                                                                     | `notify`                      |
| `connections.studioNotifyHost`                         | The name of the DocSpace Studio Notify service                                                                              | `studio-notify`               |
| `connections.socketHost`                               | The name of the DocSpace Socket service                                                                                     | `socket`                      |
| `connections.peopleServerHost`                         | The name of the DocSpace People Server service                                                                              | `people-server`               |
| `connections.filesHost`                                | The name of the DocSpace Files service                                                                                      | `files`                       |
| `connections.filesServicesHost`                        | The name of the DocSpace Files Services service                                                                             | `files-services`              |
| `connections.studioHost`                               | The name of the DocSpace Studio service                                                                                     | `studio`                      |
| `connections.backupHost`                               | The name of the DocSpace Backup service                                                                                     | `backup`                      |
| `connections.ssoauthHost`                              | The name of the DocSpace SSO service                                                                                        | `ssoauth`                     |
| `connections.clearEventsHost`                          | The name of the DocSpace Clear Events service                                                                               | `clear-events`                |
| `connections.doceditorHost`                            | The name of the DocSpace Doceditor service                                                                                  | `doceditor`                   |
| `connections.backupBackgroundTasksHost`                | The name of the DocSpace Backup Background Tasks service                                                                    | `backup-background-tasks`     |
| `connections.loginHost`                                | The name of the DocSpace Login service                                                                                      | `login`                       |
| `connections.healthchecksHost`                         | The name of the DocSpace Healthchecks service                                                                               | `healthchecks`                |
| `connections.documentServerHost`                       | The name of the Document Server service                                                                                     | `document-server`             |
| `connections.documentServerUrlPublic`                  | The name of the Document Server service                                                                                     | `/ds-vpath/`                  |
| `connections.documentServerUrlInternal`                | The name of the Document Server service for internal requests                                                               | `http://document-server/`     |
| `connections.appUrlPortal`                             | URL for DocSpace requests. By default, the name of the routing (Router) service and the port on which it accepts requests are used | `http://router:8092`   |
| `connections.appCoreBaseDomain`                        | The base domain on which the DocSpace will be available                                                                     | `localhost`                   |
| `connections.appCoreMachinekey.secretKey`              | The secret key used in the DocSpace                                                                                         | `your_core_machinekey`        |
| `connections.appCoreMachinekey.existingSecret`         | The name of an existing secret containing Core Machine Key. Must contain the `APP_CORE_MACHINEKEY` key. If not specified, a secret will be created with the value set in `connections.appCoreMachinekey.secretKey` | `""` |
| `connections.countWorkerConnections`                   | Defines the nginx config [worker_connections](https://nginx.org/en/docs/ngx_core_module.html#worker_connections) directive for routing (Router) service | `1024` |
| `connections.nginxSnvsubstTemplateSuffix`              | A suffix of template files for rendering nginx configs in routing (Router) service                                          | `.template`                   |
| `connections.appKnownNetworks`                         | Defines the address ranges of known networks to accept forwarded headers from for DocSpace services. In particular, the networks in which the proxies that you are using in front of DocSpace services are located should be indicated here. Provide IP ranges using CIDR notation | `10.244.0.0/16` |
| `connections.oauthRedirectURL`                         | Address of the oauth authorization server                                                                                   | `https://service.onlyoffice.com/oauth2.aspx` |
| `namespaceOverride`                                    | The name of the namespace in which DocSpace will be deployed. If not set, the name will be taken from `.Release.Namespace`  | `""`                          |
| `commonLabels`                                         | Defines labels that will be additionally added to all the deployed resources. You can also use `tpl` as the value for the key | `{}`                        |
| `podAnnotations`                                       | Map of annotations to add to the DocSpace pods                                                                              | `rollme: "{{ randAlphaNum 5 \| quote }}"` |
| `serviceAccount.create`                                | Enable ServiceAccount creation                                                                                              | `false`                       |
| `serviceAccount.name`                                  | Name of the ServiceAccount to be used. If not set and `serviceAccount.create` is `true` the name will be taken from `.Release.Name` or `serviceAccount.create` is `false` the name will be "default" | `""` |
| `serviceAccount.annotations`                           | Map of annotations to add to the ServiceAccount                                                                             | `{}`                          |
| `serviceAccount.automountServiceAccountToken`          | Enable auto mount of ServiceAccountToken on the serviceAccount created. Used only if `serviceAccount.create` is `true`      | `true`                        |
| `podSecurityContext.enabled`                           | Enable security context for the pods. If set to true, `podSecurityContext` is enabled for all resources describing the podTemplate. Individual values for `docs` and `opensearch` | `false`                |
| `podSecurityContext.runAsUser`                         | User ID for the DocSpace pods. Individual values for `docs` and `opensearch`                                             | `104`                         |
| `podSecurityContext.runAsGroup`                        | Group ID for the DocSpace pods. Individual values for `docs` and `opensearch`                                                            | `107`                         |
| `containerSecurityContext.enabled`                     | Enable security context for containers in pods                                                                              | `false`                       |
| `containerSecurityContext.allowPrivilegeEscalation`    | Controls whether a process can gain more privileges than its parent process                                                 | `false`                       |
| `nodeSelector`                                         | Node labels for pods assignment                                                                                             | `{}`                          |
| `tolerations`                                          | Tolerations for pods assignment                                                                                             | `[]`                          |
| `imagePullSecrets`                                     | Container image registry secret name                                                                                        | `""`                          |
| `images.tag`                                           | Global image tag for all services. Does not apply to the Document Server and Proxy Frontend                                 | `2.0.3`                       |
| `jwt.enabled`                                          | Specifies the enabling the JSON Web Token validation by the DocSpace                                                        | `true`                        |
| `jwt.secret`                                           | Defines the secret key to validate the JSON Web Token in the request to the DocSpace                                        | `jwt_secret`                  |
| `jwt.header`                                           | Defines the http header that will be used to send the JSON Web Token                                                        | `AuthorizationJwt`            |
| `jwt.inBody`                                           | Specifies the enabling the token validation in the request body to the DocSpace                                             | `false`                       |
| `jwt.existingSecret`                                   | The name of an existing secret containing variables for jwt. If not specified, a secret named `jwt` will be created         | `""`                          |
| `extraConf.secretName`                                 | The name of the Secret containing the json files that override the default values and additional configuration files        | `""`                          |
| `extraConf.filename`                                   | The name of the json files that contains custom values and name additional configuration files. Must be the same as the `key` name in `extraConf.secretName`. May contain multiple values | `appsettings.test.json` |
| `log.level`                                            | Defines the type and severity of a logged event                                                                             | `Warning`                     |
| `debug.enabled`                                        | Enable debug                                                                                                                | `false`                       |
| `initContainers.checkDB.image.repository`              | check-db initContainer image repository                                                                                     | `onlyoffice/docs-utils`                                                               |
| `initContainers.checkDB.image.tag`                     | check-db initContainer image tag. If set to, it takes priority over the `images.tag`                                        | `7.5.1-2`                                                                             |
| `initContainers.checkDB.image.pullPolicy`              | check-db initContainer image pull policy                                                                                    | `IfNotPresent`                                                                        |
| `initContainers.checkDB.resources.requests.memory`     | The requested Memory for the check-db initContainer                                                                         | `256Mi`                                                                               |
| `initContainers.checkDB.resources.requests.cpu`        | The requested CPU for the check-db initContainer                                                                            | `100m`                                                                                |
| `initContainers.checkDB.resources.limits.memory`       | The Memory limits for the check-db initContainer                                                                            | `1Gi`                                                                                 |
| `initContainers.checkDB.resources.limits.cpu`          | The CPU limits for the check-db initContainer                                                                               | `1000m`                                                                               |
| `initContainers.waitStorage.image.repository`          | app-wait-storage initContainer image repository                                                                             | `onlyoffice/docspace-wait-bin-share`                                                  |
| `initContainers.waitStorage.image.tag`                 | app-wait-storage initContainer image tag. If set to, it takes priority over the `images.tag`                                | `""`                                                                                  |
| `initContainers.waitStorage.image.pullPolicy`          | app-wait-storage initContainer image pull policy                                                                            | `IfNotPresent`                                                                        |
| `initContainers.waitStorage.resources.requests.memory` | The requested Memory for the app-wait-storage initContainer                                                             | `256Mi`                                                                               |
| `initContainers.waitStorage.resources.requests.cpu`    | The requested CPU for the app-wait-storage initContainer                                                                | `100m`                                                                                |
| `initContainers.waitStorage.resources.limits.memory`   | The Memory limits for the app-wait-storage initContainer                                                                | `1Gi`                                                                                 |
| `initContainers.waitStorage.resources.limits.cpu`      | The CPU limits for the app-wait-storage initContainer                                                                   | `1000m`                                                                               |
| `initContainers.initStorage.image.repository`          | app-init-storage initContainer image repository                                                                             | `onlyoffice/docspace-bin-share`                                                       |
| `initContainers.initStorage.image.tag`                 | app-init-storage initContainer image tag. If set to, it takes priority over the `images.tag`                                | `""`                                                                                  |
| `initContainers.initStorage.image.pullPolicy`          | app-init-storage initContainer image pull policy                                                                            | `IfNotPresent`                                                                        |
| `initContainers.initStorage.resources.requests.memory` | The requested Memory for the app-init-storage initContainer                                                             | `256Mi`                                                                               |
| `initContainers.initStorage.resources.requests.cpu`    | The requested CPU for the app-init-storage initContainer                                                                | `100m`                                                                                |
| `initContainers.initStorage.resources.limits.memory`   | The Memory limits for the app-init-storage initContainer                                                                | `2Gi`                                                                                 |
| `initContainers.initStorage.resources.limits.cpu`      | The CPU limits for the app-init-storage initContainer                                                                   | `1000m`                                                                               |
| `initContainers.custom`                                | Defines custom containers that run before DocSpace containers in a Pods. For example, a container that changes the owner of the PersistentVolume. For the `Document Server`, `Router`, `Opensearch` and `Proxy Frontend` services, the corresponding individual parameters are used | `[]` |
| `persistence.storageClass`                             | PVC Storage Class for DocSpace data volume                                                                              | `nfs`                                                                                 |
| `persistence.docspaceData.existingClaim`               | The name of the existing PVC for storing files common to all services. If not specified, a PVC named "docspace-data" will be created | `""`                                                                     |
| `persistence.docspaceData.size`                        | PVC Storage Request for common files volume                                                                             | `8Gi`                                                                                 |
| `persistence.filesData.existingClaim`                  | The name of the existing PVC for use in the Files service. If not specified, a PVC named "files-data" will be created   | `""`                                                                                  |
| `persistence.filesData.size`                           | PVC Storage Request for Files volume                                                                                    | `2Gi`                                                                                 |
| `persistence.peopleData.existingClaim`                 | The name of the existing PVC for use in the People Server service. If not specified, a PVC named "people-data" will be created | `""`                                                                           |
| `persistence.peopleData.size`                          | PVC Storage Request for People Server volume                                                                            | `2Gi`                                                                                 |
| `persistence.routerLog.existingClaim`                  | The name of the existing PVC for storing Nginx logs of the Router service. If not specified, a PVC named "router-log" will be created | `""`                                                                      |
| `persistence.routerLog.size`                           | PVC Storage Request for Nginx logs volume                                                                               | `5Gi`                                                                                 |
| `podAntiAffinity.type`                                 | Types of Pod antiaffinity. Allowed values: `preferred` or `required`                                                    | `preferred`                                                                           |
| `podAntiAffinity.topologyKey`                          | Node label key to match                                                                                                 | `kubernetes.io/hostname`                                                              |
| `podAntiAffinity.weight`                               | Priority when selecting node. It is in the range from 1 to 100. Used only when `podAntiAffinity.type=preferred`         |`100`                                                                                  |

### DocSpace Application* parameters

| Parameter                                                 | Description                                                                                                     | Default                                   |
|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| `Application.enabled`                                     | Enables Application installation. Individual value for the `apiSystem`                                          | `true`                                    |
| `Application.kind`                                        | The controller used for deploy. Possible values are `Deployment` (default) or `StatefulSet`. Not used in `docs` and `opensearch` | `Deployment`          |
| `Application.replicaCount`                                | Number of "Application" replicas to deploy                                                                      | `1`                                       |
| `Application.updateStrategy.type`                         | "Application" update strategy type                                                                              | `RollingUpdate`                           |
| `Application.updateStrategy.rollingUpdate.maxUnavailable` | Maximum number of "Application" Pods unavailable during the update process                                      | `25%`                                     |
| `Application.updateStrategy.rollingUpdate.maxSurge`       | Maximum number of "Application" Pods created over the desired number of Pods                                    | `25%`                                     |
| `Application.podManagementPolicy`                         | The Application Pods scaling operations policy. Used if `Application.kind` is set to `StatefulSet`. Not used in `docs` and `opensearch` | `OrderedReady` |
| `Application.podAffinity`                                 | Defines [Pod affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity) rules for "Application" Pods scheduling by nodes relative to other Pods | `{}` |
| `Application.nodeAffinity`                                | Defines [Node affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) rules for "Application" Pods scheduling by nodes | `{}` |
| `Application.image.repository`                            | "Application" container image repository. Individual values for `proxyFrontend`, `docs` and `opensearch`     | `onlyoffice/docspace-Application`         |
| `Application.image.tag`                                   | "Application" container image tag. If set to, it takes priority over the `images.tag`. Individual values for `proxyFrontend`, `docs` and `opensearch` | `""`          |
| `Application.image.pullPolicy`                            | "Application" container image pull policy                                                                       | `IfNotPresent`                            |
| `Application.containerPorts.app`                          | "Application" container port. Not used in `router`, `login` and `proxyFrontend`                                 | `5050`                                    |
| `Application.startupProbe.enabled`                        | Enable startupProbe for "Application" container                                                                 | `true`                                    |
| `Application.readinessProbe.enabled`                      | Enable readinessProbe for "Application" container                                                               | `true`                                    |
| `Application.livenessProbe.enabled`                       | Enable livenessProbe for "Application" container                                                                | `true`                                    |
| `Application.resources.requests`                          | The requested resources for the "Application" container                                                         | `memory, cpu`                             |
| `Application.resources.limits`                            | The resources limits for the "Application" container                                                            | `memory, cpu`                             |

* Application* Note: Since all available Applications have some identical parameters, a description for each of them has not been added to the table, but combined into one.
Instead of `Application`, the parameter name should have the following values: `files`, `peopleServer`, `router`, `healthchecks`, `apiSystem`, `api`, `backup`, `backupBackgroundTasks`, 
`clearEvents`, `doceditor`, `filesServices`, `login`, `notify`, `socket`, `ssoauth`, `studio`, `studioNotify`, `proxyFrontend`, `docs` and `opensearch`.

### DocSpace Router Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `router.initContainers`                                  | Defines containers that run before Router container in the Router pod                                           | `[]`                 |
| `router.containerPorts.external`                         | Router container port                                                                                           | `8092`               |
| `router.extraConf.customInitScripts.configMap`           | The name of the ConfigMap containing custom initialization scripts                                              | `""`                 |
| `router.extraConf.customInitScripts.fileName`            | The names of scripts containing custom initialization scripts. Must be the same as the `key` names in `router.extraConf.customInitScripts.configMap`. May contain multiple values | `60-custom-init-scripts.sh` |
| `router.extraConf.templates.configMap`                   | The name of the ConfigMap containing configuration file templates containing environment variables. The values of these variables will be substituted when the container is started | `""` |
| `router.extraConf.templates.fileName`                    | The names of the configuration file templates containing environment variables. Must be the same as the `key` names in `router.extraConf.templates.configMap`. May contain multiple values | `10.example.conf.template` |
| `router.extraConf.confd.configMap`                       | The name of the ConfigMap containing additional custom configuration files. These files will be map in the `/etc/nginx/conf.d/` directory of the container | `""` |
| `router.extraConf.confd.fileName`                        | The names of the configuration files containing custom configuration files. Must be the same as the `key` names in `router.extraConf.confd.configMap`. May contain multiple values | `example.conf` |
| `router.service.existing`                                | The name of an existing service for Router. If not set, a service named `router` will be created                | `""`                 |
| `router.service.annotations`                             | Map of annotations to add to the Router service                                                                 | `{}`                 |
| `router.service.port.external`                           | Router service port                                                                                             | `8092`               |
| `router.service.type`                                    | Router service type                                                                                             | `ClusterIP`          |
| `router.service.sessionAffinity`                         | [Session Affinity](https://kubernetes.io/docs/reference/networking/virtual-ips/#session-affinity) for Router service. If not set, `None` will be set as the default value | `""` |
| `router.service.sessionAffinityConfig`                   | [Configuration](https://kubernetes.io/docs/reference/networking/virtual-ips/#session-stickiness-timeout) for Router service Session Affinity. Used if the `router.service.sessionAffinity` is set | `{}` |
| `router.service.externalTrafficPolicy`                   | Enable preservation of the client source IP. There are two [available options](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip): `Cluster` (default) and `Local`. Not [supported](https://kubernetes.io/docs/tutorials/services/source-ip/) for service type - `ClusterIP` | `""` |
| `router.resolver.dns`                                    | [Configures](https://github.com/openresty/openresty/#resolvconf-parsing) name server used to resolve names of upstream servers into addresses. If set to, it takes priority over the `router.resolver.local` | `""` |
| `router.resolver.local`                                  | Allows you to use the DNS configuration of the container. If set to `on`, the standard path "/etc/resolv.conf" will be used. You can specify an arbitrary path | `on` |

### DocSpace Api System Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `apiSystem.enabled`                                      | Enables Api System installation                                                                                 | `false`              |

### DocSpace Doceditor Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `doceditor.containerPorts.doceditor`                     | Doceditor container port                                                                                        | `5013`               |

### DocSpace Login Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `login.containerPorts.login`                             | Login container port                                                                                            | `5011`               |

### DocSpace Socket Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `socket.containerPorts.socket`                           | Socket additional container port                                                                                | `9899`               |

### DocSpace Ssoauth Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `ssoauth.containerPorts.sso`                             | Ssoauth additional container port                                                                               | `9834`               |

### DocSpace Proxy Frontend Application additional parameters

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `proxyFrontend.enabled`                                  | Enables Proxy Frontend installation                                                                             | `false`              |
| `proxyFrontend.initContainers`                           | Defines containers that run before Proxy Frontend container in the Proxy Frontend pod                           | `[]`                 |
| `proxyFrontend.image.repository`                         | Proxy Frontend container image repository                                                                       | `nginx`              |
| `proxyFrontend.image.tag`                                | Proxy Frontend container image tag                                                                              | `latest`             |
| `proxyFrontend.containerPorts.http`                      | Proxy Frontend HTTP container port                                                                              | `80`                 |
| `proxyFrontend.containerPorts.https`                     | Proxy Frontend HTTPS container port                                                                             | `443`                |
| `proxyFrontend.extraConf.customConfd.configMap`          | The name of the ConfigMap containing additional custom configuration files. These files will be map in the `/etc/nginx/conf.d/` directory of the container | `""` |
| `proxyFrontend.extraConf.customConfd.fileName`           | The names of the configuration files containing additional custom configuration files. Must be the same as the `key` names in `proxyFrontend.extraConf.customConfd.configMap`. May contain multiple values | `example.conf` |
| `proxyFrontend.hostname`                                 | The hostname (domainname) by which the DocSpace will be available                                               | `""`                 |
| `proxyFrontend.tls.secretName`                           | The name of the TLS secret containing the certificate and its associated key                                    | `tls`                |
| `proxyFrontend.tls.mountPath`                            | The path where the certificate and key will be mounted                                                          | `/etc/nginx/ssl`     |
| `proxyFrontend.tls.crtName`                              | Name of the key containing the certificate                                                                      | `cert.crt`           |
| `proxyFrontend.tls.keyName`                              | Name of the key containing the key                                                                              | `cert.key`           |
| `proxyFrontend.service.existing`                         | The name of an existing service for Proxy Frontend. If not set, a service named `proxy-frontend` will be created | `""`                |
| `proxyFrontend.service.annotations`                      | Map of annotations to add to the Proxy Frontend service                                                         | `{}`                 |
| `proxyFrontend.service.type`                             | Proxy Frontend service type                                                                                     | `LoadBalancer`       |
| `proxyFrontend.service.sessionAffinity`                  | [Session Affinity](https://kubernetes.io/docs/reference/networking/virtual-ips/#session-affinity) for Proxy Frontend. service. If not set, `None` will be set as the default value | `""` |
| `proxyFrontend.service.sessionAffinityConfig`            | [Configuration](https://kubernetes.io/docs/reference/networking/virtual-ips/#session-stickiness-timeout) for Proxy Frontend service Session Affinity. Used if the `proxyFrontend.service.sessionAffinity` is set | `{}` |
| `proxyFrontend.service.externalTrafficPolicy`            | Enable preservation of the client source IP. There are two [available options](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip): `Cluster` (default) and `Local`. Not [supported](https://kubernetes.io/docs/tutorials/services/source-ip/) for service type - `ClusterIP` | `""` |

### DocSpace Document Server StatefulSet additional parameters

NOTE: It is recommended to use an installation made specifically for Kubernetes. See more details about installing ONLYOFFICE Docs in Kubernetes via Helm [here](https://github.com/ONLYOFFICE/Kubernetes-Docs)

| Parameter                                                | Description                                                                                                     | Default              |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| `docs.enabled`                                           | Enables local installation of Document Server in k8s cluster                                                    | `true`                |
| `docs.podSecurityContext.enabled`                        | Enable security context for the Document Server Pod                                                             | `false`               |
| `docs.podSecurityContext.runAsUser`                      | User ID for the Document Server pod                                                                             | `101`                 |
| `docs.podSecurityContext.runAsGroup`                     | Group ID for the Document Server pod                                                                            | `101`                 |
| `docs.initContainers`                                    | Defines containers that run before Document Server container in the Document Server pod                         | `[]`                  |
| `docs.image.repository`                                  | Document Server container image repository                                                                      | `onlyoffice/documentserver` |
| `docs.image.tag`                                         | Document Server container image tag                                                                             | `7.4.0`               |
| `docs.containerPorts.http`                               | Document Server HTTP container port                                                                             | `80`                  |
| `docs.containerPorts.https`                              | Document Server HTTPS container port                                                                            | `443`                 |
| `docs.containerPorts.docservice`                         | Document Server docservice container port                                                                       | `8000`                |

### DocSpace Ingress parameters

| Parameter                                                | Description                                                                                                     | Default                                                                                   |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| `ingress.enabled`                                        | Enable the creation of an ingress for the DocSpace                                                              | `false`                                                                                   |
| `ingress.annotations`                                    | Map of annotations to add to the Ingress                                                                        | `kubernetes.io/ingress.class: nginx`, `nginx.ingress.kubernetes.io/proxy-body-size: 100m` |
| `ingress.ingressClassName`                               | Used to reference the IngressClass that should be used to implement this Ingress                                | `nginx`                                                                                   |
| `ingress.tls.enabled`                                    | Enable TLS for the DocSpace                                                                                     | `false`                                                                                   |
| `ingress.tls.secretName`                                 | Secret name for TLS to mount into the Ingress                                                                   | `tls`                                                                                     |
| `ingress.host`                                           | Ingress hostname for the DocSpace                                                                               | `""`                                                                                      |

### DocSpace Jobs parameters

| Parameter                                                       | Description                                                                                                                                                                                                | Default                                         |
|-----------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `install.job.enabled`                                           | Enable the execution of job pre-install before installing DocSpace                                                                                                                                         | `true`                                          |
| `install.job.podAffinity`                                       | Defines [Pod affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity) rules for Install Job Pod scheduling by nodes relative to other Pods | `{}`                                            |
| `install.job.nodeAffinity`                                      | Defines [Node affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) rules for Install Job Pod scheduling by nodes                                              | `{}`                                            |
| `install.job.initContainers.migrationRunner.enabled`            | Enable database initialization                                                                                                                                                                             | `true`                                          |
| `install.job.initContainers.migrationRunner.image.repository`   | Job by pre-install Migration Runner container image repository                                                                                                                                             | `onlyoffice/docspace-migration-runner`          |
| `install.job.initContainers.migrationRunner.image.tag`          | Job by pre-install Migration Runner container image tag. If set to, it takes priority over the `images.tag`                                                                                                | `""`                                            |
| `install.job.initContainers.migrationRunner.image.pullPolicy`   | Job by pre-install Migration Runner container image pull policy                                                                                                                                            | `IfNotPresent`                                  |
| `install.job.initContainers.migrationRunner.resources.requests` | The requested resources for the Job pre-install Migration Runner container                                                                                                                                 | `memory, cpu`                                   |
| `install.job.initContainers.migrationRunner.resources.limits`   | The resources limits for the Job pre-install Migration Runner container                                                                                                                                    | `memory, cpu`                                   |
| `upgrade.job.enabled`                                           | Enable the execution of job pre-upgrade before upgrading DocSpace                                                                                                                                          | `true`                                          |
| `upgrade.job.podAffinity`                                       | Defines [Pod affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity) rules for Upgrade Job Pod scheduling by nodes relative to other Pods | `{}`                                            |
| `upgrade.job.nodeAffinity`                                      | Defines [Node affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#node-affinity) rules for Upgrade Job Pod scheduling by nodes                                              | `{}`                                            |
| `upgrade.job.initContainers.migrationRunner.enabled`            | Enable database update                                                                                                                                                                                     | `true`                                          |
| `upgrade.job.initContainers.migrationRunner.image.repository`   | Job by pre-upgrade Migration Runner container image repository                                                                                                                                             | `onlyoffice/docspace-migration-runner`          |
| `upgrade.job.initContainers.migrationRunner.image.tag`          | Job by pre-upgrade Migration Runner container image tag. If set to, it takes priority over the `images.tag`                                                                                                | `""`                                            |
| `upgrade.job.initContainers.migrationRunner.image.pullPolicy`   | Job by pre-upgrade Migration Runner container image pull policy                                                                                                                                            | `IfNotPresent`                                  |
| `upgrade.job.initContainers.migrationRunner.resources.requests` | The requested resources for the Job pre-upgrade Migration Runner container                                                                                                                                 | `memory, cpu`                                   |
| `upgrade.job.initContainers.migrationRunner.resources.limits`   | The resources limits for the Job pre-upgrade Migration Runner container                                                                                                                                    | `memory, cpu`                                   |

### DocSpace Opensearch parameters

| Parameter                                                | Description                                                                                                     | Default                    |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------|
| `opensearch.enabled`                                  | Enables Opensearch installation                                                                              | `true`                     |
| `opensearch.podSecurityContext.enabled`               | Enable security context for the Opensearch Pod                                                               | `false`                    |
| `opensearch.podSecurityContext.runAsUser`             | User ID for the Opensearch pod                                                                               | `1000`                     |
| `opensearch.podSecurityContext.runAsGroup`            | Group ID for the Opensearch pod                                                                              | `1000`                     |
| `opensearch.initContainers`                           | Defines containers that run before Opensearch container in the Opensearch pod                                | `[]`                       |
| `opensearch.image.repository`                         | Opensearch container image repository                                                                        | `onlyoffice/opensearch` |
| `opensearch.image.tag`                                | Opensearch container image tag                                                                               | `7.16.3`                   |
| `opensearch.containerSecurityContext.enabled`         | Enable security context for Opensearch container in pod                                                      | `false`                    |
| `opensearch.containerSecurityContext.privileged`      | Granting a privileged status to the Opensearch container                                                     | `false`                    |
| `opensearch.persistence.storageClass`                 | PVC Storage Class for Opensearch volume                                                                      | `"nfs"`                    |
| `opensearch.persistence.accessModes`                  | Opensearch Persistent Volume access modes                                                                    | `ReadWriteOnce`            |
| `opensearch.persistence.size`                         | PVC Storage Request for Opensearch volume                                                                    | `30Gi`                     |
| `opensearch.env.discoveryType`                        | Determines the cluster discovery type. Set to "single-node" for a single-node cluster                        | `single-node               |
| `opensearch.env.disableSecurityPlugin`                | disables the security plugin                                                                                 | `true`                     |
| `opensearch.env.disableInstallDemoConfig`             | disables the installation of demo configuration                                                              | `true`                     |
| `opensearch.env.bootstrapMemoryLock`                  | determines whether JVM should lock memory                                                                    | `true`                     |
| `opensearch.env.ESJAVAOPTS`                           | defines JVM options                                                                                          | `-Xms2g -Xmx2g -Dlog4j2.formatMsgNoLookups=true`               |
| `opensearch.env.indicesFieldDataCacheSize`            | sets the size of the index field data cache                                                                  | `30%`                      |
| `opensearch.env.indicesMemoryIndexBufferSize`         | sets the size of the in-memory index buffer                                                                  | `30%`                      |

### DocSpace Test parameters

| Parameter                                                | Description                                                                                                     | Default                    |
|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------|
| `tests.enabled`                                          | Enable the resources creation necessary for DocSpace launch testing and connected dependencies availability testing. These resources will be used when running the `helm test` command | `true`                           |
| `tests.podSecurityContext.enabled`                       | Enable security context for the Test pod                                                                                                                                               | `false`                          |
| `tests.podSecurityContext.runAsUser`                     | User ID for the Test pod                                                                                                                                                               | `0`                              |
| `tests.podSecurityContext.runAsGroup`                    | Group ID for the Test pod                                                                                                                                                              | `0`                              |
| `tests.resources.requests`                               | The requested resources for the test container                                                                                                                                         | `memory: "256Mi"`, `cpu: "200m"` |
| `tests.resources.limits`                                 | The resources limits for the test container                                                                                                                                            | `memory: "1Gi"`, `cpu: "1000m"`  |

## Configuration and installation details

### 1. Expose DocSpace

#### 1.1 Expose DocSpace via Service (HTTP Only)

*You should skip step[#1.1] if you are going to expose DocSpace via HTTPS*

This type of exposure has the least overheads of performance, it creates a loadbalancer to get access to DocSpace.
Use this type of exposure if you use external TLS termination, and don't have another WEB application in the k8s cluster.

To expose DocSpace via service, set the `router.service.type` parameter to `LoadBalancer`:

```bash
$ helm install [RELEASE_NAME] onlyoffice/docspace --set router.service.type=LoadBalancer,router.service.port.external=8092

```

Run the following command to get the `DocSpace` service IP:

```bash
$ kubectl get service router -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```

After that, DocSpace will be available at `http://DOCSPACE-SERVICE-IP/`.

If the service IP is empty, try getting the `DocSpace` service hostname:

```bash
$ kubectl get service router -o jsonpath="{.status.loadBalancer.ingress[*].hostname}"
```

In this case, DocSpace will be available at `http://DOCSPACE-SERVICE-HOSTNAME/`.


#### 1.2 Expose DocSpace via Ingress

#### 1.2.1 Installing the Kubernetes Nginx Ingress Controller

To install the Nginx Ingress Controller to your cluster, run the following command:

```bash
$ helm install nginx-ingress ingress-nginx/ingress-nginx --set controller.publishService.enabled=true,controller.replicaCount=2
```

See more detail about installing Nginx Ingress Controller via Helm [here](https://github.com/kubernetes/ingress-nginx/tree/master/charts/ingress-nginx).

#### 1.2.2 Expose DocSpace via HTTP

*You should skip step[2.1.2] if you are going to expose DocSpace via HTTPS*

This type of exposure has more overheads of performance compared with exposure via service, it also creates a loadbalancer to get access to DocSpace.
Use this type if you use external TLS termination and when you have several WEB applications in the k8s cluster. You can use the one set of ingress instances and the one loadbalancer for those. It can optimize the entry point performance and reduce your cluster payments, cause providers can charge a fee for each loadbalancer.

To expose DocSpace via ingress HTTP, set the `ingress.enabled` parameter to true:

```bash
$ helm install [RELEASE_NAME] onlyoffice/docspace --set ingress.enabled=true

```

Run the following command to get the `docspace` ingress IP:

```bash
$ kubectl get ingress docspace -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```

After that, DocSpace will be available at `http://DOCSPACE-INGRESS-IP/`.

If the ingress IP is empty, try getting the `docspace` ingress hostname:

```bash
$ kubectl get ingress docspace -o jsonpath="{.status.loadBalancer.ingress[*].hostname}"
```

In this case, DocSpace will be available at `http://DOCSPACE-INGRESS-HOSTNAME/`.

#### 1.2.3 Expose DocSpace via HTTPS

This type of exposure allows you to enable internal TLS termination for DocSpace.

Create the `tls` secret with an ssl certificate inside.

Put the ssl certificate and the private key into the `tls.crt` and `tls.key` files and then run:

```bash
$ kubectl create secret generic tls \
  --from-file=./tls.crt \
  --from-file=./tls.key
```

```bash
$ helm install [RELEASE_NAME] onlyoffice/docspace --set ingress.enabled=true,ingress.tls.enabled=true,ingress.tls.secretName=tls,ingress.host=example.com

```

Run the following command to get the `docspace` ingress IP:

```bash
$ kubectl get ingress docspace -o jsonpath="{.status.loadBalancer.ingress[*].ip}"
```

If the ingress IP is empty, try getting the `docspace` ingress hostname:

```bash
$ kubectl get ingress docspace -o jsonpath="{.status.loadBalancer.ingress[*].hostname}"
```

Associate the `docspace` ingress IP or hostname with your domain name through your DNS provider.

After that, DocSpace will be available at `https://your-domain-name/`.

### 2. Transition from ElasticSearch to OpenSearch

In DocSpace appVersion 2.5.0, ElasticSearch is being replaced with OpenSearch, which will require reindexing, taking some time.

For proper reindexing before updating DocSpace to version 2.5.0, execute the following command:
- If `file-services` is deployed as a StatefulSet:

  ```bash
  kubectl scale statefulset files-services --replicas=0
  ```
- Otherwise, if deployed as a Deployment:

  ```bash
  kubectl scale deployment files-services --replicas=0
  ```
Then proceed with the DocSpace update.

NOTE: If you have an external Elasticsearch installed, please follow these steps before updating:

1. Reduce the replica count of `files-services` to 0, as described above.
2. In the configmap and job files named `remove-indexes-manually.yml`, replace the values in `spec.template.spec.containers.env[(name=="MYSQL_PASSWORD")].value` and, if necessary, in `spec.template.spec.containers.env[(name=="MYSQL_USER")].value` with your own values.
3. Apply these files `remove-indexes-manually.yml`:

  ```bash
  kubectl apply -fhttps://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-DocSpace/main/sources/remove-indexes-manually.yaml
  ```
After successfully executing the Pod `remove-indexes` that created the Job, delete this Job with the following command:

  ``` bash
  kubectl delete -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-DocSpace/main/sources/remove-indexes-manually.yaml
  ```
## DocSpace installation test (optional)

You can test DocSpace services availability and access to connected dependencies by running the following command:

```bash
$ helm test [RELEASE_NAME] -n <NAMESPACE>
```

The output should have the following line:

```bash
Phase: Succeeded
```

To view the log of the Pod running as a result of the `helm test` command, run the following command:

```bash
$ kubectl logs -f test-docspace -n <NAMESPACE>
```

The DocSpace services availability check is considered a priority, so if it fails with an error, the test is considered to be failed.

After this, you can delete the `test-docspace` Pod by running the following command:

```bash
$ kubectl delete pod test-docspace -n <NAMESPACE>
```

Note: This testing is for informational purposes only and cannot guarantee 100% availability results.
It may be that even though all checks are completed successfully, an error occurs in the application.
In this case, more detailed information can be found in the application logs.
