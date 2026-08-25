# Exposing ONLYOFFICE DocSpace via Gateway API

As an alternative to the classic [Ingress](../README.md#12-expose-onlyoffice-docspace-via-ingress), ONLYOFFICE DocSpace can be exposed via the [Gateway API](https://gateway-api.sigs.k8s.io/) by setting the `gateway.enabled` parameter to `true`. All Gateway API settings live under the `gateway.*` block.

## Prerequisites

Before you begin, install the Gateway API CRDs and a controller. For [NGINX Gateway Fabric](https://docs.nginx.com/nginx-gateway-fabric/) (GatewayClass `nginx`), follow its official [installation guide](https://docs.nginx.com/nginx-gateway-fabric/install/helm/). If you want a different Gateway API implementation, install it according to its own docs and set the `gateway.gatewayClassName` parameter accordingly.

## Expose ONLYOFFICE DocSpace via HTTP

To expose ONLYOFFICE DocSpace via the Gateway API over HTTP, set the `gateway.enabled` and the `gateway.host` parameters:

```bash
$ helm install [RELEASE_NAME] onlyoffice/docspace --set gateway.enabled=true --set gateway.host=docspace.example.com
```

Note: The `gateway.host` field is optional. Access is also possible by IP address.

Run the following command to get the Gateway address:

```bash
$ kubectl get gateway [RELEASE_NAME]-gateway -o jsonpath="{.status.addresses[*].value}"
```

Associate the Gateway address with your domain name through your DNS provider.

In this case, ONLYOFFICE DocSpace will be available at `http://docspace.example.com/`.

## Expose ONLYOFFICE DocSpace via HTTPS

This type of exposure allows you to enable internal TLS termination for ONLYOFFICE DocSpace.

Create the `tls-gw` secret with an ssl certificate inside. Put the ssl certificate and the private key into the `tls.crt` and `tls.key` files and then run:

```bash
$ kubectl create secret tls tls-gw \
  --cert=./tls.crt \
  --key=./tls.key
```

```bash
$ helm install [RELEASE_NAME] onlyoffice/docspace --set gateway.enabled=true,gateway.ssl.enabled=true,gateway.host=docspace.example.com
```

The `gateway.host` or `gateway.tenants` field is required.

Run the following command to get the Gateway address:

```bash
$ kubectl get gateway [RELEASE_NAME]-gateway -o jsonpath="{.status.addresses[*].value}"
```

Associate the Gateway address with your domain name through your DNS provider.

After that, ONLYOFFICE DocSpace will be available at `https://your-domain-name/`.

## Expose ONLYOFFICE DocSpace via HTTPS using the Let's Encrypt certificate

- Add Helm repositories:
  ```bash
  $ helm repo add jetstack https://charts.jetstack.io
  $ helm repo update
  ```
- Installing cert-manager with Gateway API support enabled:
  ```bash
  $ helm install cert-manager --version v1.20.2 jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set crds.enabled=true \
    --set crds.keep=false \
    --set config.enableGatewayAPI=true
  ```

Note: Install the Gateway API CRDs (see [Prerequisites](#prerequisites)) before cert-manager, or restart cert-manager afterwards — it only checks for Gateway API support on startup.

The `config.enableGatewayAPI=true` flag is required so that cert-manager reconciles Gateway resources and creates temporary HTTPRoutes for the ACME HTTP-01 challenge.

Next, perform the installation by setting the `gateway.enabled`, `gateway.ssl.enabled` and `gateway.letsencrypt.enabled` parameters to `true`. Also set your own values in the `gateway.letsencrypt.email` and `gateway.host` parameters (or `gateway.tenants`, for example `--set "gateway.tenants={tenant1.example.com,tenant2.example.com}"`, if you want to use multiple domain names):

```bash
$ helm install [RELEASE_NAME] onlyoffice/docspace \
  --set gateway.enabled=true \
  --set gateway.ssl.enabled=true \
  --set gateway.letsencrypt.enabled=true \
  --set gateway.letsencrypt.email=you@example.com \
  --set gateway.host=docspace.example.com
```

The chart creates a `ClusterIssuer`, and cert-manager solves the ACME HTTP-01 challenge through the Gateway, writing the issued certificate into the Secret named in `gateway.ssl.secret`. Run the following command to view the state of the certificate issuing:

```bash
$ kubectl describe certificate <gateway.ssl.secret>
```

After that, ONLYOFFICE DocSpace will be available at `https://your-domain-name/`.

## Optional HTTP to HTTPS redirect

To redirect all HTTP traffic to HTTPS, set the `gateway.ssl.redirect.enabled` parameter to `true` (requires `gateway.ssl.enabled=true`). A second `HTTPRoute` is created on the HTTP listener(s) that redirects to HTTPS with the status code from `gateway.ssl.redirect.statusCode` (default `301`).

## Attach to an external Gateway

To attach ONLYOFFICE DocSpace to a `Gateway` managed outside this chart, set the `gateway.external.parentRefs` parameter — in this case the chart does not create its own `Gateway`. Set the `gateway.external.redirectParentRefs` parameter as well if you want the chart to also manage the HTTP to HTTPS redirect route on that Gateway:

```yaml
gateway:
  enabled: true
  ssl:
    enabled: true
    redirect:
      enabled: true
  external:
    parentRefs:
      - name: <GATEWAY_NAME>
        namespace: <GATEWAY_NAMESPACE>
        sectionName: https
    redirectParentRefs:
      - name: <GATEWAY_NAME>
        namespace: <GATEWAY_NAMESPACE>
        sectionName: http
```

## Client settings (NGINX Gateway Fabric)

The `gateway.clientSettingsPolicy` parameter renders a `ClientSettingsPolicy` attached to the ONLYOFFICE DocSpace `HTTPRoute`. By default it raises the maximum request body size to `100m`, which is useful for large file uploads:

```yaml
gateway:
  clientSettingsPolicy:
    body:
      maxSize: 100m
```

Set the `gateway.clientSettingsPolicy` parameter to `{}` or `null` to skip it. This is specific to NGINX Gateway Fabric and is ignored by other Gateway controllers.
