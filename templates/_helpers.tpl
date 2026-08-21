{{/*
Check the Installation type
*/}}
{{- define "apps.installation.type" -}}
{{- $installationType := .Values.global.installationType -}}
{{- $possibleInstallationTypes := list "DEVELOPER" "ENTERPRISE" -}}
{{- if has $installationType $possibleInstallationTypes }}
    {{- $installationType -}}
{{- else -}}
    {{- fail "You have specified an unsupported Installation type! Possible values: DEVELOPER or ENTERPRISE" -}}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps Namespace
*/}}
{{- define "apps.namespace" -}}
{{- if .Values.namespaceOverride -}}
    {{- .Values.namespaceOverride -}}
{{- else -}}
    {{- .Release.Namespace -}}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps labels
*/}}
{{- define "apps.labels.commonLabels" -}}
{{- range $key, $value := .Values.commonLabels }}
{{ $key }}: {{ tpl $value $ }}
{{- end }}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps annotations
*/}}
{{- define "apps.annotations" -}}
{{- $annotations := toYaml .keyName }}
{{- if contains "{{" $annotations }}
    {{- tpl $annotations .context }}
{{- else }}
    {{- $annotations }}
{{- end }}
{{- end -}}

{{/*
Get the update strategy type for ONLYOFFICE Apps
*/}}
{{- define "apps.update.strategyType" -}}
{{- if eq .type "RollingUpdate" -}}
    {{- toYaml . | nindent 4 -}}
{{- else -}}
    {{- omit . "rollingUpdate" | toYaml | nindent 4 -}}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps Service Account name
*/}}
{{- define "apps.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default .Release.Name .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps Identity Service Account name
*/}}
{{- define "apps.identity.serviceAccountName" -}}
{{- if .Values.identity.serviceAccount.create -}}
    {{- printf "identity-sa" -}}
{{- else if .Values.identity.serviceAccount.name -}}
    {{ .Values.identity.serviceAccount.name }}
{{- else -}}
    {{ include "apps.serviceAccountName" . }}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps Security Context
*/}}
{{- define "apps.securityContext" -}}
{{- if not .seLinuxOptions -}}
    {{- omit . "enabled" "seLinuxOptions" | toYaml }}
{{- else -}}
    {{- omit . "enabled" | toYaml }}
{{- end -}}
{{- end -}}

{{/*
A function to return correct registry.
*/}}
{{- define "apps.imageRegistry" -}}
{{- $context := index . 0 -}}
{{- $registry := coalesce (index . 1) $context.Values.images.registry -}}
{{- if $registry }}
    {{- printf "%s/" ($registry | trimSuffix "/") -}}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps image repository
*/}}
{{- define "apps.imageRepository" -}}
{{- $context := index . 0 -}}
{{- $repo := index . 1 -}}
{{- $repoPrefix := $context.Values.images.repoPrefix -}}
{{- $repoProductName := $context.Values.product.name -}}
{{- if and $repoPrefix (eq $repoPrefix "4testing" ) (contains (printf "%s/" $repoProductName) $repo) -}}
    {{- $repo | replace (printf "%s/" $repoProductName) (printf "%s/%s-" $repoProductName $repoPrefix) -}}
{{- else if $repoPrefix }}
    {{- $repo | replace (printf "%s/" $repoProductName) (printf "%s/" $repoPrefix) -}}
{{- else -}}
    {{- $repo -}}
{{- end -}}
{{- end -}}

{{/*
Get the MySQL password secret
*/}}
{{- define "apps.mysql.secretName" -}}
{{- if .Values.connections.mysqlPassword -}}
    {{- printf "%s-mysql" .Release.Name -}}
{{- else if .Values.connections.mysqlExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.mysqlExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for MySQL
*/}}
{{- define "apps.mysql.createSecret" -}}
{{- if or .Values.connections.mysqlPassword (not .Values.connections.mysqlExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return MySQL password
*/}}
{{- define "apps.mysql.password" -}}
{{- if not (empty .Values.connections.mysqlPassword) }}
    {{- .Values.connections.mysqlPassword }}
{{- else -}}
    {{- required "A MySQL Password is required!" .Values.connections.mysqlPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Redis password secret
*/}}
{{- define "apps.redis.secretName" -}}
{{- if or .Values.connections.redisPassword .Values.connections.redisNoPass -}}
    {{- printf "%s-redis" .Release.Name -}}
{{- else if .Values.connections.redisExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.redisExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Redis
*/}}
{{- define "apps.redis.createSecret" -}}
{{- if or .Values.connections.redisPassword .Values.connections.redisNoPass (not .Values.connections.redisExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Redis password
*/}}
{{- define "apps.redis.password" -}}
{{- if not (empty .Values.connections.redisPassword) }}
    {{- .Values.connections.redisPassword }}
{{- else if .Values.connections.redisNoPass }}
    {{- printf "" }}
{{- else }}
    {{- required "A Redis Password is required!" .Values.connections.redisPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Broker password secret
*/}}
{{- define "apps.broker.secretName" -}}
{{- if .Values.connections.brokerPassword -}}
    {{- printf "%s-broker" .Release.Name -}}
{{- else if .Values.connections.brokerExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.brokerExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Broker
*/}}
{{- define "apps.broker.createSecret" -}}
{{- if or .Values.connections.brokerPassword (not .Values.connections.brokerExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Broker password
*/}}
{{- define "apps.broker.password" -}}
{{- if not (empty .Values.connections.brokerPassword) }}
    {{- .Values.connections.brokerPassword }}
{{- else }}
    {{- required "A Broker Password is required!" .Values.connections.brokerPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Broker URI
*/}}
{{- define "apps.broker.uri" -}}
{{- $brokerSecret := include "apps.broker.secretName" . }}
{{- $secretKey := (lookup "v1" "Secret" .Release.Namespace $brokerSecret).data }}
{{- $keyValue := (get $secretKey .Values.connections.brokerSecretKeyName) | b64dec }}
{{- if .Values.connections.brokerUri -}}
    {{- printf "%s" .Values.connections.brokerUri -}}
{{- else if $keyValue -}}
    {{- printf "%s://%s:%s@%s:%s%s" .Values.connections.brokerProto .Values.connections.brokerUser $keyValue .Values.connections.brokerHost .Values.connections.brokerPort .Values.connections.brokerVhost -}}
{{- else if .Values.connections.brokerPassword -}}
    {{- printf "%s://%s:%s@%s:%s%s" .Values.connections.brokerProto .Values.connections.brokerUser .Values.connections.brokerPassword .Values.connections.brokerHost .Values.connections.brokerPort .Values.connections.brokerVhost -}}
{{- else if not .Values.connections.brokerPassword -}}
    {{- required "A Broker user Password is required!" .Values.connections.brokerPassword -}}
{{- end -}}
{{- end -}}

{{/*
Get the ONLYOFFICE Apps Url Portal
*/}}
{{- define "apps.url.portal" -}}
{{- if empty .Values.connections.appUrlPortal -}}
    {{- printf "" -}}
{{- else if and .Values.connections.documentServerUrlExternal .Values.router.service.existing -}}
    {{- printf "%s" (tpl .Values.connections.appUrlPortal $) -}}
{{- else if and .Values.router.service.existing (not .Values.connections.documentServerUrlExternal) -}}
    {{- printf "http://%s:%s" (tpl .Values.router.service.existing $) (toString .Values.router.service.port.external) -}}
{{- else if not (empty .Values.connections.appUrlPortal) -}}
    {{- printf "%s" (tpl .Values.connections.appUrlPortal $) -}}
{{- else -}}
    {{- printf "http://router:%s" (toString .Values.router.service.port.external) -}}
{{- end -}}
{{- end -}}

{{/*
Get the jwt secret name
*/}}
{{- define "apps.jwt.secretName" -}}
{{- if .Values.jwt.existingSecret -}}
    {{- printf "%s" (tpl .Values.jwt.existingSecret $) -}}
{{- else }}
    {{- printf "docspace-jwt" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for jwt
*/}}
{{- define "apps.jwt.createSecret" -}}
{{- if empty .Values.jwt.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get a secret name containing Core Machine Key
*/}}
{{- define "apps.coreMachineKey.secretName" -}}
{{- if .Values.connections.appCoreMachinekey.existingSecret -}}
    {{- printf "%s" (tpl .Values.connections.appCoreMachinekey.existingSecret $) -}}
{{- else }}
    {{- printf "%s-core-machine-key" .Release.Name -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Core Machine Key
*/}}
{{- define "apps.coreMachineKey.createSecret" -}}
{{- if empty .Values.connections.appCoreMachinekey.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Core Machine Key
*/}}
{{- define "apps.secret.coreMachineKey" -}}
{{- if not (empty .Values.connections.appCoreMachinekey.secretKey) }}
    {{- .Values.connections.appCoreMachinekey.secretKey }}
{{- else }}
    {{- required "A Core Machine Key is required!" .Values.connections.appCoreMachinekey.secretKey }}
{{- end }}
{{- end -}}

{{/*
Return resolver for ONLYOFFICE Apps Router
*/}}
{{- define "apps.router.resolver" -}}
{{- if .Values.router.resolver.dns -}}
    {{- .Values.router.resolver.dns -}}
{{- else -}}
    {{- printf "local=%s" (toString .Values.router.resolver.local) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a service object should be created for ONLYOFFICE Apps Router
*/}}
{{- define "apps.svc.router.create" -}}
{{- if empty .Values.router.service.existing }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the service name for ONLYOFFICE Apps Router
*/}}
{{- define "apps.svc.router.name" -}}
{{- if .Values.router.service.existing -}}
    {{- printf "%s" (tpl .Values.router.service.existing $) -}}
{{- else -}}
    {{- printf "router" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a service object should be created for ONLYOFFICE Apps Proxy Frontend
*/}}
{{- define "apps.svc.proxyFrontend.create" -}}
{{- if empty .Values.proxyFrontend.service.existing }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the service name for ONLYOFFICE Apps Proxy Frontend
*/}}
{{- define "apps.svc.proxyFrontend.name" -}}
{{- if .Values.proxyFrontend.service.existing -}}
    {{- printf "%s" (tpl .Values.proxyFrontend.service.existing $) -}}
{{- else -}}
    {{- printf "proxy-frontend" -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for ONLYOFFICE Apps Data
*/}}
{{- define "apps.pvc.data.name" -}}
{{- if .Values.persistence.docspaceData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.docspaceData.existingClaim $) -}}
{{- else }}
    {{- printf "docspace-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for ONLYOFFICE Apps Data
*/}}
{{- define "apps.pvc.data.create" -}}
{{- if empty .Values.persistence.docspaceData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for ONLYOFFICE Apps Router log
*/}}
{{- define "apps.pvc.router.name" -}}
{{- if .Values.persistence.routerLog.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.routerLog.existingClaim $) -}}
{{- else }}
    {{- printf "router-log" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for ONLYOFFICE Apps Router log
*/}}
{{- define "apps.pvc.router.create" -}}
{{- if empty .Values.persistence.routerLog.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Identity
*/}}
{{- define "apps.identity.createSecret" -}}
{{- if empty .Values.identity.secret.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get a secret name containing Spring encryption secret
*/}}
{{- define "apps.identity.secretName" -}}
  {{- if .Values.identity.secret.existingSecret -}}
    {{- printf "%s" (tpl .Values.identity.secret.existingSecret $) -}}
  {{- else -}}
    {{- "docspace-identity" -}}
  {{- end -}}
{{- end -}}

{{/*
Generate a random 512-bit secret if the secret does not already exist
*/}}
{{- define "apps.generateSecret" -}}
{{- $context := index . 0 -}}
{{- $existValue := index . 1 -}}
{{- $getSecretName := index . 2 -}}
{{- $getSecretKey := index . 3 -}}
{{- if not $existValue }}
    {{- $secret_lookup := (lookup "v1" "Secret" $context.Release.Namespace $getSecretName).data }}
    {{- $getSecretValue := (get $secret_lookup $getSecretKey) | b64dec }}
    {{- if $getSecretValue -}}
        {{- printf "%s" $getSecretValue -}}
    {{- else -}}
        {{- printf "%s" (randAlphaNum 64) -}}
    {{- end -}}
{{- else -}}
    {{- printf "%s" $existValue -}}
{{- end -}}
{{- end -}}

{{/*
Determine what value to pass to generateSecret for SPRING_APPLICATION_ENCRYPTION_SECRET
*/}}
{{- define "apps.identity.springEncryptionValue" -}}
{{- $val := .Values.identity.secret.springEncryptionValue }}
{{- if and $val (ne $val "") }}
  {{- $val }}
{{- else if eq (.Values.identity.secret.generate | toString) "true" }}
  {{- "" }}
{{- else }}
  {{- "secret" }}
{{- end }}
{{- end }}

{{/*
Defines the APP_CORE_SERVER_ROOT value for single-portal setups
*/}}
{{- define "apps.singlePortalDomain.appCoreServerRoot" -}}
{{- if .Values.ingress.tls.enabled }}
https://*/
{{- else if .Values.singlePortalDomain.job.env.appCoreServerRoot }}
{{ .Values.singlePortalDomain.job.env.appCoreServerRoot }}
{{- else }}
{{ "" }}
{{- end }}
{{- end }}

{{/*
Get the domain for single-portal setups
*/}}
{{- define "apps.singlePortalDomain.domain" -}}
{{- if .Values.ingress.host }}
{{ .Values.ingress.host }}
{{- else if .Values.singlePortalDomain.job.env.domain }}
{{ .Values.singlePortalDomain.job.env.domain }}
{{- end }}
{{- end }}

{{/*
Get the Gateway name for ONLYOFFICE Apps
*/}}
{{- define "apps.gateway.name" -}}
{{- default (printf "%s-gateway" .Release.Name) .Values.gateway.name }}
{{- end }}