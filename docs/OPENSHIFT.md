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
> The `pre-upgrade` job runs a `rootless` init container that needs UID 0, which no non-root SCC allows. On OpenShift the volume ownership is handled by `fsGroup`, so disable it: `--set upgrade.job.initContainers.rootless.enabled=false`.

## Publish ONLYOFFICE Apps via Route
To expose ONLYOFFICE Apps outside the OpenShift cluster, you can use an OpenShift Route. It is created for the `router` service. To enable route creation, set the following parameters:
```bash
--set openshift.route.enabled=true \
--set openshift.route.host=<HOSTNAME>
```

By default the Route terminates TLS with the default certificate of the OpenShift ingress controller. To use your own certificate, see [Configure TLS for the Route](#configure-tls-for-the-route).

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
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
    # Optional. Without it the default certificate of the OpenShift ingress controller is used
    externalCertificate:
      name: <SECRET_NAME>
```

## Configure TLS for the Route
The Route terminates TLS (`edge`) and redirects HTTP to HTTPS. Without a certificate it uses the default certificate of the OpenShift ingress controller.

To use your own certificate (OpenShift 4.19+), create a `kubernetes.io/tls` Secret in the release namespace **before** the installation, the API rejects a Route that refers to a missing Secret. Then pass its name:
```bash
--set openshift.route.tls.existingSecret=<SECRET_NAME>
```

The chart also creates a Role and RoleBinding that let the OpenShift router read the Secret. Set `openshift.route.tls.rbac.create=false` to manage them yourself.

### Your own certificate
```bash
oc create secret tls <SECRET_NAME> --cert=tls.crt --key=tls.key -n <NAMESPACE>
```

### Let's Encrypt via cert-manager
Create the issuer and the certificate yourself before installing ONLYOFFICE Apps. cert-manager renews the certificate in the same Secret and the router picks it up, no `helm upgrade` is needed.

> [!IMPORTANT]
> cert-manager v1.18+ must run with the `ACMEHTTP01IngressPathTypeExact=false` feature gate, and `<HOSTNAME>` must be reachable on port 80 from the Internet (HTTP-01).

Install cert-manager with the feature gate if it is not installed yet:
```bash
helm repo add jetstack https://charts.jetstack.io
helm upgrade --install cert-manager jetstack/cert-manager -n cert-manager --create-namespace \
  --set crds.enabled=true \
  --set featureGates=ACMEHTTP01IngressPathTypeExact=false
```

`issuer.yaml` (replace `<EMAIL>`). For several namespaces use a `ClusterIssuer`: the same spec without `namespace`. For tests use the staging server `https://acme-staging-v02.api.letsencrypt.org/directory`:
```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-prod
  namespace: <NAMESPACE>
spec:
  acme:
    email: <EMAIL>
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - http01:
        ingress:
          ingressClassName: openshift-default
```

`certificate.yaml` (`secretName` is the value for `existingSecret`, use `kind: ClusterIssuer` for a `ClusterIssuer`):
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: docspace-route-tls
  namespace: <NAMESPACE>
spec:
  secretName: docspace-route-tls
  dnsNames:
  - <HOSTNAME>
  privateKey:
    rotationPolicy: Always
  issuerRef:
    kind: Issuer
    name: letsencrypt-prod
```

Apply them and wait for the certificate:
```bash
oc apply -f issuer.yaml -f certificate.yaml
oc wait certificate/docspace-route-tls -n <NAMESPACE> --for=condition=Ready --timeout=10m
```

Install ONLYOFFICE Apps with the Secret (see the [example install command](#example-install-command)) and check the result:
```bash
--set openshift.route.enabled=true \
--set openshift.route.host=<HOSTNAME> \
--set openshift.route.tls.existingSecret=docspace-route-tls
```
```bash
oc get route docspace -n <NAMESPACE> -o jsonpath='{.spec.tls.externalCertificate}'
echo | openssl s_client -connect <HOSTNAME>:443 -servername <HOSTNAME> -verify_return_error 2>&1 | grep -E "issuer=|Verify return code"
```

## Example install command

> [!IMPORTANT]
> Deployment of dependencies such as RabbitMQ, Redis, and Database is not included in the example below. Make sure to deploy them first or set the corresponding parameters to use external services.

> [!NOTE]
> The Redis host must be set as the FQDN of the service. The default value points to the `default` namespace, so set `connections.redisHost` for the namespace you install into.

> [!NOTE]
> The example uses the default certificate of the OpenShift ingress controller for the Route. To use your own certificate, create the Secret first and add `--set openshift.route.tls.existingSecret=<SECRET_NAME>`, see [Configure TLS for the Route](#configure-tls-for-the-route).

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
  --set upgrade.job.initContainers.rootless.enabled=false \
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
