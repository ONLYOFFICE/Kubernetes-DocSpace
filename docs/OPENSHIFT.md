# ONLYOFFICE Apps on OpenShift 4.x

## Security Context Constraints (SCC)
> [!NOTE]
> OpenShift enforces strict security policies on pods. ONLYOFFICE Apps requires a compatible SCC because its containers run with non-root UIDs — the ONLYOFFICE Apps application containers as UID 104 and the bundled ONLYOFFICE Docs subchart (`docs.enabled=true`) as UID 101 — but some SCCs may conflict with these requirements. Therefore, we recommend assigning the `scc-docspace-components`, `nonroot-v2` or `anyuid` SCC to the relevant service accounts.

The chart ships two SCCs in [`sources/scc`](../sources/scc). They cover different workloads and are applied independently — apply only the one you need, or both if you install the external dependencies into the same cluster:

| SCC | File | UID range | Covers | Apply when |
|-----|------|-----------|--------|------------|
| `scc-docspace-components` | [`docspace-components.yaml`](../sources/scc/docspace-components.yaml) | `101`-`1001` | the ONLYOFFICE Apps application containers (UID 104) and the bundled ONLYOFFICE Docs subchart (UID 101) | always, for the ONLYOFFICE Apps release. Recommended |
| `scc-helm-components` | [`helm-components.yaml`](../sources/scc/helm-components.yaml) | `1000`-`1001` | the external dependencies (MySQL, RabbitMQ, Redis) installed via the bitnami Helm charts | only if you install those dependencies yourself. Skip it when you connect to external services |

> [!NOTE]
> The `101`-`1001` range of `scc-docspace-components` already covers the `1000`-`1001` range of `scc-helm-components`, so technically one SCC could serve both. They are kept separate on purpose: the dependencies are a different trust boundary, are often installed by a different user and into a different namespace, and granting them the wider range would hand the bitnami pods UIDs they never need. Do not grant `scc-docspace-components` to the dependency service accounts.

## Assign SCC to service accounts
> [!NOTE]
> By default `serviceAccount.create` is `false`, so the pods run under the namespace `default` service account (the bundled Docs subchart also uses `default` plus `wopi-sa`, and the Identity services use `identity-sa`). Granting the SCC to the `system:authenticated` group covers all of them at once.

> [!IMPORTANT]
> If required, enable the `podSecurityContext` and/or `containerSecurityContext` settings. Use the table below to check compatibility:

| SCC | podSecurityContext | containerSecurityContexts | Result |
|----------------|----------------------|----------------------------|--------|
| privileged | enabled | enabled | ✅Works |
| privileged | enabled | disabled | ✅Works |
| privileged | disabled | enabled | ✅Works |
| privileged | disabled | disabled | ❌Doesn't |
| nonroot | enabled | enabled | ❌Doesn't |
| nonroot | enabled | disabled | ❌Doesn't |
| nonroot | disabled | enabled | ❌Doesn't |
| nonroot | disabled | disabled | ❌Doesn't |
| nonroot-v2 | enabled | enabled | ✅Works |
| nonroot-v2 | enabled | disabled | ❌Doesn't |
| nonroot-v2 | disabled | enabled | ✅Works |
| nonroot-v2 | disabled | disabled | ❌Doesn't |
| anyuid | enabled | enabled | ❌Doesn't |
| anyuid | enabled | disabled | ✅Works |
| anyuid | disabled | enabled | ❌Doesn't |
| anyuid | disabled | disabled | ✅Works |
| scc-docspace-components | enabled | enabled | ✅Works |
| scc-docspace-components | enabled | disabled | ✅Works |
| scc-docspace-components | disabled | enabled | ✅Works |
| scc-docspace-components | disabled | disabled | ✅Works |

If you selected one of the default SCCs, assign it to the service accounts.

> [!IMPORTANT]
> You must have `cluster-admin` privileges to manage SCCs.

If you chose `scc-docspace-components` (recommended), apply it and grant it:

```bash
oc apply -f sources/scc/docspace-components.yaml
oc adm policy add-scc-to-group scc-docspace-components system:authenticated
```

If you chose one of the built-in SCCs, assign it the same way:

```bash
oc adm policy add-scc-to-group nonroot-v2 system:authenticated
```

## Set the SCC annotation in the chart
When several SCCs are available to a service account, OpenShift may not pick the intended one. To force it, set the `openshift.io/required-scc` annotation. In ONLYOFFICE Apps the annotation must be set on the pods, so use `podAnnotations`.

To apply the required SCC to all ONLYOFFICE Apps application pods:
```bash
--set podAnnotations."openshift\.io/required-scc"="scc-docspace-components"
```

For the bundled ONLYOFFICE Docs subchart:
```bash
--set docs.commonAnnotations."openshift\.io/required-scc"="scc-docspace-components"
```

## Enable security contexts
If you assigned an SCC that requires the pod to declare its user (e.g. `nonroot-v2`), enable the security contexts in the chart. With `scc-docspace-components`, which assigns a UID from its range automatically, this step is optional.

To enable them for ONLYOFFICE Apps (covers all application pods and containers):

```bash
--set podSecurityContext.enabled=true \
--set containerSecurityContext.enabled=true
```

To enable them for the bundled ONLYOFFICE Docs subchart, per component/job that you run:
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

> [!NOTE]
> The ONLYOFFICE Apps `pre-upgrade` job runs a `rootless` init container (a `chown` that needs UID 0), which no non-root SCC allows. On OpenShift the volume ownership is handled by `fsGroup`, so disable it: `--set upgrade.job.initContainers.rootless.enabled=false`.

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
  wildcardPolicy: None
  to:
    kind: Service
    name: router
    weight: 100
  port:
    targetPort: 8092
```

## Example install command

> [!IMPORTANT]
> Deployment of dependencies such as RabbitMQ, Redis, and Database not included in the example below. Make sure to deploy them first or set the corresponding parameters to use external services.

Complete example of deploying ONLYOFFICE Apps on OpenShift with the `scc-docspace-components` SCC and a route enabled:

```bash
# execute with a user who has cluster-admin permissions
oc apply -f sources/scc/docspace-components.yaml
oc adm policy add-scc-to-group scc-docspace-components system:authenticated
oc adm policy who-can use scc scc-docspace-components
# then, install the chart with any user
helm install apps onlyoffice/apps \
  --set openshift.route.enabled=true \
  --set openshift.route.host=<HOSTNAME> \
  --set podSecurityContext.enabled=true \
  --set containerSecurityContext.enabled=true \
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
