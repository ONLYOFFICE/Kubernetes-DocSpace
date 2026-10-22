# ONLYOFFICE Apps on OpenShift 4.x

## Security Context Constraints (SCC)
> [!NOTE]
> OpenShift enforces strict security policies on pods. ONLYOFFICE Apps requires a compatible SCC because its containers run with non-root UIDs — the application containers as UID 104 and the bundled ONLYOFFICE Docs subchart as UID 101, but some SCCs may conflict with these requirements. Therefore, we recommend assigning the [scc-docspace-components](../sources/scc/docspace-components.yaml) SCC to the relevant service accounts.

The chart ships two SCCs in [`sources/scc`](../sources/scc): `scc-docspace-components` over UID `101`-`1001` for the release itself, and `scc-helm-components` over UID `1000`-`1001` for the external dependencies installed from the bitnami Helm charts. They are applied and granted separately, so use only the one you need.

> [!WARNING]
> Install ONLYOFFICE Apps into a dedicated project. SCCs are not enforced in highly privileged projects such as `default`, `kube-system` and `kube-public`, so an installation there does not reflect how the pods run in a regular project.

## Assign SCC to service accounts
> [!NOTE]
> By default `serviceAccount.create` is `false`, so the pods run under the namespace `default` service account. The `wopi-sa` service account is created by the bundled ONLYOFFICE Docs subchart, and `identity-sa` is used when `identity.serviceAccount.create` is set to `true`.

> [!IMPORTANT]
> You must have `cluster-admin` privileges to manage SCCs.

Apply `scc-docspace-components` and grant it to the service accounts:

```bash
oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-Apps/main/sources/scc/docspace-components.yaml
oc adm policy add-scc-to-user scc-docspace-components -z default -z wopi-sa
```

The external dependencies (MySQL, RabbitMQ, Redis) installed from the bitnami Helm charts use a separate SCC. Grant it to the service accounts created by these charts (`mysql`, `rabbitmq` and `redis-master` for the release names used in the [README](../README.md#deploy-prerequisites)):

```bash
oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-Apps/main/sources/scc/helm-components.yaml
oc adm policy add-scc-to-user scc-helm-components -z mysql -z rabbitmq -z redis-master
```

> [!IMPORTANT]
> `add-scc-to-user -z` grants the SCC inside the current project, so run it after switching to the namespace you install into (`oc project <NAMESPACE>`).

## Set the SCC annotation in the chart
The `openshift.io/required-scc` annotation must be set on the pods, so use `podAnnotations`.

To apply the required SCC to all ONLYOFFICE Apps pods:
```bash
--set podAnnotations."openshift\.io/required-scc"="scc-docspace-components"
```

For the bundled ONLYOFFICE Docs subchart:
```bash
--set docs.commonAnnotations."openshift\.io/required-scc"="scc-docspace-components"
```

OpenSearch does not use the global `podAnnotations`, so set the annotation for it separately:
```bash
--set opensearch.podAnnotations."openshift\.io/required-scc"="scc-docspace-components"
```

## Enable security contexts
If you assigned an SCC that requires security contexts, enable them in the chart. With `scc-docspace-components` the `containerSecurityContext` is required: otherwise the SCC assigns UID `101` to the containers, and the ONLYOFFICE Apps containers that run as UID `104` fail to start. The `podSecurityContext` is recommended: it sets the `fsGroup` to the application group `107`, without it the SCC assigns the `fsGroup` from its range.

To enable `podSecurityContext` and `containerSecurityContext`:

```bash
--set podSecurityContext.enabled=true \
--set containerSecurityContext.enabled=true
```

To enable them for the bundled ONLYOFFICE Docs subchart:
```bash
--set docs.podSecurityContext.enabled=true \
--set docs.docservice.containerSecurityContext.enabled=true \
--set docs.proxy.containerSecurityContext.enabled=true \
--set docs.converter.containerSecurityContext.enabled=true \
--set docs.wopiKeysGeneration.job.containerSecurityContext.enabled=true \
--set docs.wopiKeysDeletion.job.containerSecurityContext.enabled=true \
--set docs.install.job.containerSecurityContext.enabled=true \
--set docs.upgrade.job.containerSecurityContext.enabled=true \
--set docs.delete.job.containerSecurityContext.enabled=true \
--set docs.rollback.job.containerSecurityContext.enabled=true \
--set docs.clearCache.job.containerSecurityContext.enabled=true \
--set docs.customResources.job.containerSecurityContext.enabled=true
```

OpenSearch has its own security contexts and runs as UID `1000`. Its `change-volume-owner` init container needs UID 0, so disable it, the volume ownership is handled by `fsGroup`:
```bash
--set opensearch.podSecurityContext.enabled=true \
--set opensearch.containerSecurityContext.enabled=true \
--set opensearch.initContainers.changeVolumeOwner.enabled=false
```

> [!NOTE]
> If you are upgrading from a chart version earlier than `2.4.0`, whose images ran as root, do not enable `upgrade.job.initContainers.rootless.enabled`: its init container needs UID 0, which no non-root SCC allows. The volume ownership is handled by `fsGroup` from the `podSecurityContext`. If your storage does not support `fsGroup` (for example, NFS), change the owner of the `docspace-data` and `router-log` volumes to `104:107` manually before the upgrade.

## Publish ONLYOFFICE Apps via Route
To expose ONLYOFFICE Apps outside the OpenShift cluster, you can use an OpenShift Route. It is created for the `router` service. To enable route creation, set the following parameters:
```bash
--set openshift.route.enabled=true \
--set openshift.route.host=<HOSTNAME>
```

> [!WARNING]
> TLS configuration is not managed by the chart. Configure TLS manually in the console after installation.

> [!TIP]
> For reference, here is an example route configuration. Use it as a template if you need to create or modify the route manually:

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: docspace
  namespace: <NAMESPACE>
spec:
  host: <HOSTNAME>
  path: /
  wildcardPolicy: <WILDCARD_POLICY>
  to:
    kind: Service
    name: router
    weight: 100
  port:
    targetPort: 8092
```

## Example install command

> [!IMPORTANT]
> Deployment of dependencies such as RabbitMQ, Redis, and Database is not included in the example below. Make sure to deploy them first or set the corresponding parameters to use external services.

> [!NOTE]
> The Redis host must be set as the FQDN of the service. The default value points to the `default` namespace, so set `connections.redisHost` for the namespace you install into.

Complete example of deploying ONLYOFFICE Apps on OpenShift with the `scc-docspace-components` SCC and route enabled:

```bash
# execute with a user who has cluster-admin permissions
oc new-project <NAMESPACE>
oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-Apps/main/sources/scc/docspace-components.yaml
oc adm policy add-scc-to-user scc-docspace-components -z default -z wopi-sa
oc adm policy who-can use scc scc-docspace-components
# then, install the chart with any user
helm install apps onlyoffice/apps -n <NAMESPACE> \
  --set connections.redisHost=redis-master.<NAMESPACE>.svc.cluster.local \
  --set openshift.route.enabled=true \
  --set openshift.route.host=<HOSTNAME> \
  --set podAnnotations."openshift\.io/required-scc"="scc-docspace-components" \
  --set docs.commonAnnotations."openshift\.io/required-scc"="scc-docspace-components" \
  --set opensearch.podAnnotations."openshift\.io/required-scc"="scc-docspace-components" \
  --set podSecurityContext.enabled=true \
  --set containerSecurityContext.enabled=true \
  --set opensearch.podSecurityContext.enabled=true \
  --set opensearch.containerSecurityContext.enabled=true \
  --set opensearch.initContainers.changeVolumeOwner.enabled=false \
  --set docs.podSecurityContext.enabled=true \
  --set docs.docservice.containerSecurityContext.enabled=true \
  --set docs.proxy.containerSecurityContext.enabled=true \
  --set docs.converter.containerSecurityContext.enabled=true \
  --set docs.wopiKeysGeneration.job.containerSecurityContext.enabled=true \
  --set docs.wopiKeysDeletion.job.containerSecurityContext.enabled=true \
  --set docs.install.job.containerSecurityContext.enabled=true \
  --set docs.upgrade.job.containerSecurityContext.enabled=true \
  --set docs.delete.job.containerSecurityContext.enabled=true \
  --set docs.rollback.job.containerSecurityContext.enabled=true \
  --set docs.clearCache.job.containerSecurityContext.enabled=true \
  --set docs.customResources.job.containerSecurityContext.enabled=true
```
