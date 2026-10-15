# ONLYOFFICE Apps on OpenShift 4.x

## Security Context Constraints (SCC)
> [!NOTE]
> OpenShift enforces strict security policies on pods. ONLYOFFICE Apps requires a compatible SCC because its containers run with non-root UIDs — the application containers as UID 104 and the bundled ONLYOFFICE Docs subchart as UID 101, but some SCCs may conflict with these requirements. Therefore, we recommend assigning the `nonroot-v2`, `anyuid` or [scc-docspace-components](../sources/scc/docspace-components.yaml) SCC to the relevant service accounts.

The chart ships two SCCs in [`sources/scc`](../sources/scc): `scc-docspace-components` over UID `101`-`1001` for the release itself, and `scc-helm-components` over UID `1000`-`1001` for the external dependencies installed from the bitnami Helm charts. They are applied and granted separately, so use only the one you need.

## Assign SCC to service accounts
> [!NOTE]
> By default `serviceAccount.create` is `false`, so the pods run under the namespace `default` service account. The `wopi-sa` service account is created by the bundled ONLYOFFICE Docs subchart, and `identity-sa` is used when `identity.serviceAccount.create` is set to `true`.

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

```bash
oc adm policy add-scc-to-user <SCC-name> -z default -z wopi-sa
```

If you chose `scc-docspace-components`, apply it and then grant it:

```bash
oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-Apps/main/sources/scc/docspace-components.yaml
oc adm policy add-scc-to-user scc-docspace-components -z default -z wopi-sa
```

The external dependencies (MySQL, RabbitMQ, Redis) installed from the bitnami Helm charts use a separate SCC:

```bash
oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-Apps/main/sources/scc/helm-components.yaml
oc adm policy add-scc-to-user scc-helm-components -z default
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

## Enable security contexts
If you assigned an SCC that requires security contexts, enable them in the chart. With `scc-docspace-components` this step is optional, because the SCC assigns a UID from its range automatically.

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

> [!NOTE]
> The `pre-upgrade` job runs a `rootless` init container that needs UID 0, which no non-root SCC allows. On OpenShift the volume ownership is handled by `fsGroup`, so disable it: `--set upgrade.job.initContainers.rootless.enabled=false`.

## Publish ONLYOFFICE Apps via Route
To expose ONLYOFFICE Apps outside the OpenShift cluster, you can use an OpenShift Route. It is created for the `router` service. To enable route creation, set the following parameters:
```bash
--set openshift.route.enabled=true \
--set openshift.route.host=<HOSTNAME>
```

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

## Configure TLS for the Route
TLS is terminated on the Route (`edge`) and HTTP is redirected to HTTPS. If no certificate is set, the Route uses the default certificate of the OpenShift ingress controller.

> [!IMPORTANT]
> Your own certificate and Let's Encrypt use the Route `spec.tls.externalCertificate` field, so OpenShift 4.19+ is required. The chart creates a Role and RoleBinding that let the OpenShift router read the certificate Secret (`openshift.route.tls.rbac.create`).

To use your own certificate, create a Secret of type `kubernetes.io/tls` in the namespace of the Route before the installation and set its name:
```bash
oc create secret tls docspace-tls --cert=tls.crt --key=tls.key -n <NAMESPACE>
```
```bash
--set openshift.route.tls.existingSecret=docspace-tls
```

To issue a Let's Encrypt certificate via [cert-manager](https://cert-manager.io/docs/installation/) (ACME HTTP-01):
```bash
--set openshift.route.tls.letsencrypt.enabled=true \
--set openshift.route.tls.letsencrypt.email=<EMAIL>
```

The `openshift.route.host` must have a public DNS record pointing to the OpenShift ingress controller, with port 80 reachable from the Internet. By default the chart creates a namespaced `Issuer`. To use an existing issuer, set `openshift.route.tls.letsencrypt.issuer.create=false` and its `kind` and `name`.

> [!IMPORTANT]
> cert-manager v1.18+ must run with the `ACMEHTTP01IngressPathTypeExact=false` feature gate. Otherwise OpenShift does not convert the challenge Ingress into a Route and the certificate is never issued:
> ```bash
> helm upgrade cert-manager jetstack/cert-manager -n cert-manager --reuse-values --set featureGates=ACMEHTTP01IngressPathTypeExact=false
> ```

> [!NOTE]
> The API rejects a Route that refers to a missing Secret, so on the first installation the Route uses the default certificate. When the Certificate is Ready, run the upgrade again to attach it to the Route:
> ```bash
> oc wait certificate/docspace --for=condition=Ready --timeout=10m -n <NAMESPACE>
> helm upgrade [RELEASE_NAME] onlyoffice/apps --reset-then-reuse-values --no-hooks -n <NAMESPACE>
> ```
> cert-manager then renews the certificate in the same Secret, and the router picks it up automatically.

## Example install command

> [!IMPORTANT]
> Deployment of dependencies such as RabbitMQ, Redis, and Database not included in the example below. Make sure to deploy them first or set the corresponding parameters to use external services.

Complete example of deploying ONLYOFFICE Apps on OpenShift with the `scc-docspace-components` SCC and route enabled:

```bash
# execute with a user who has cluster-admin permissions
oc apply -f https://raw.githubusercontent.com/ONLYOFFICE/Kubernetes-Apps/main/sources/scc/docspace-components.yaml
oc adm policy add-scc-to-user scc-docspace-components -z default -z wopi-sa
oc adm policy who-can use scc scc-docspace-components
# then, install the chart with any user
helm install apps onlyoffice/apps \
  --set openshift.route.enabled=true \
  --set openshift.route.host=<HOSTNAME> \
  --set podAnnotations."openshift\.io/required-scc"="scc-docspace-components" \
  --set docs.commonAnnotations."openshift\.io/required-scc"="scc-docspace-components" \
  --set upgrade.job.initContainers.rootless.enabled=false \
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
