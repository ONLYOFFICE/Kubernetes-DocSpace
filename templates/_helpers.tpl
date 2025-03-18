{{/*
Check the Installation type
*/}}
{{- define "docspace.installation.type" -}}
{{- $installationType := .Values.global.installationType -}}
{{- $possibleInstallationTypes := list "COMMUNITY" "DEVELOPER" "ENTERPRISE" -}}
{{- if has $installationType $possibleInstallationTypes }}
    {{- $installationType -}}
{{- else -}}
    {{- fail "You have specified an unsupported Installation type! Possible values: COMMUNITY, DEVELOPER and ENTERPRISE" -}}
{{- end -}}
{{- end -}}

{{/*
Get the DocSpace Namespace
*/}}
{{- define "docspace.namespace" -}}
{{- if .Values.namespaceOverride -}}
    {{- .Values.namespaceOverride -}}
{{- else -}}
    {{- .Release.Namespace -}}
{{- end -}}
{{- end -}}

{{/*
Get the DocSpace labels
*/}}
{{- define "docspace.labels.commonLabels" -}}
{{- range $key, $value := .Values.commonLabels }}
{{ $key }}: {{ tpl $value $ }}
{{- end }}
{{- end -}}

{{/*
Get the DocSpace annotations
*/}}
{{- define "docspace.annotations" -}}
{{- $annotations := toYaml .keyName }}
{{- if contains "{{" $annotations }}
    {{- tpl $annotations .context }}
{{- else }}
    {{- $annotations }}
{{- end }}
{{- end -}}

{{/*
Get the update strategy type for DocSpace Apps
*/}}
{{- define "docspace.update.strategyType" -}}
{{- if eq .type "RollingUpdate" -}}
    {{- toYaml . | nindent 4 -}}
{{- else -}}
    {{- omit . "rollingUpdate" | toYaml | nindent 4 -}}
{{- end -}}
{{- end -}}

{{/*
Get the DocSpace Service Account name
*/}}
{{- define "docspace.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default .Release.Name .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Get the DocSpace Identity Service Account name
*/}}
{{- define "docspace.identity.serviceAccountName" -}}
{{- if .Values.identity.serviceAccount.create -}}
    {{- printf "identity-sa" -}}
{{- else -}}
    {{ include "docspace.serviceAccountName" . }}
{{- end -}}
{{- end -}}

{{/*
Get the DocSpace Security Context
*/}}
{{- define "docspace.securityContext" -}}
{{- if not .seLinuxOptions -}}
    {{- omit . "enabled" "seLinuxOptions" | toYaml }}
{{- else -}}
    {{- omit . "enabled" | toYaml }}
{{- end -}}
{{- end -}}

{{/*
Get the DocSpace image repository
*/}}
{{- define "docspace.imageRepository" -}}
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
{{- define "docspace.mysql.secretName" -}}
{{- if .Values.connections.mysqlPassword -}}
    {{- printf "%s-mysql" .Release.Name -}}
{{- else if .Values.connections.mysqlExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.mysqlExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for MySQL
*/}}
{{- define "docspace.mysql.createSecret" -}}
{{- if or .Values.connections.mysqlPassword (not .Values.connections.mysqlExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return MySQL password
*/}}
{{- define "docspace.mysql.password" -}}
{{- if not (empty .Values.connections.mysqlPassword) }}
    {{- .Values.connections.mysqlPassword }}
{{- else -}}
    {{- required "A MySQL Password is required!" .Values.connections.mysqlPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Redis password secret
*/}}
{{- define "docspace.redis.secretName" -}}
{{- if or .Values.connections.redisPassword .Values.connections.redisNoPass -}}
    {{- printf "%s-redis" .Release.Name -}}
{{- else if .Values.connections.redisExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.redisExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Redis
*/}}
{{- define "docspace.redis.createSecret" -}}
{{- if or .Values.connections.redisPassword .Values.connections.redisNoPass (not .Values.connections.redisExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Redis password
*/}}
{{- define "docspace.redis.password" -}}
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
{{- define "docspace.broker.secretName" -}}
{{- if .Values.connections.brokerPassword -}}
    {{- printf "%s-broker" .Release.Name -}}
{{- else if .Values.connections.brokerExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.brokerExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Broker
*/}}
{{- define "docspace.broker.createSecret" -}}
{{- if or .Values.connections.brokerPassword (not .Values.connections.brokerExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Broker password
*/}}
{{- define "docspace.broker.password" -}}
{{- if not (empty .Values.connections.brokerPassword) }}
    {{- .Values.connections.brokerPassword }}
{{- else }}
    {{- required "A Broker Password is required!" .Values.connections.brokerPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Broker URI
*/}}
{{- define "docspace.broker.uri" -}}
{{- $brokerSecret := include "docspace.broker.secretName" . }}
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
Get the DocSpace Url Portal
*/}}
{{- define "docspace.url.portal" -}}
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
{{- define "docspace.jwt.secretName" -}}
{{- if .Values.jwt.existingSecret -}}
    {{- printf "%s" (tpl .Values.jwt.existingSecret $) -}}
{{- else }}
    {{- printf "docspace-jwt" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for jwt
*/}}
{{- define "docspace.jwt.createSecret" -}}
{{- if empty .Values.jwt.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get a secret name containing Core Machine Key
*/}}
{{- define "docspace.coreMachineKey.secretName" -}}
{{- if .Values.connections.appCoreMachinekey.existingSecret -}}
    {{- printf "%s" (tpl .Values.connections.appCoreMachinekey.existingSecret $) -}}
{{- else }}
    {{- printf "%s-core-machine-key" .Release.Name -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Core Machine Key
*/}}
{{- define "docspace.coreMachineKey.createSecret" -}}
{{- if empty .Values.connections.appCoreMachinekey.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Core Machine Key
*/}}
{{- define "docspace.secret.coreMachineKey" -}}
{{- if not (empty .Values.connections.appCoreMachinekey.secretKey) }}
    {{- .Values.connections.appCoreMachinekey.secretKey }}
{{- else }}
    {{- required "A Core Machine Key is required!" .Values.connections.appCoreMachinekey.secretKey }}
{{- end }}
{{- end -}}

{{/*
Return resolver for DocSpace Router
*/}}
{{- define "docspace.router.resolver" -}}
{{- if .Values.router.resolver.dns -}}
    {{- .Values.router.resolver.dns -}}
{{- else -}}
    {{- printf "local=%s" (toString .Values.router.resolver.local) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a service object should be created for DocSpace Router
*/}}
{{- define "docspace.svc.router.create" -}}
{{- if empty .Values.router.service.existing }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the service name for DocSpace Router
*/}}
{{- define "docspace.svc.router.name" -}}
{{- if .Values.router.service.existing -}}
    {{- printf "%s" (tpl .Values.router.service.existing $) -}}
{{- else -}}
    {{- printf "router" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a service object should be created for DocSpace Proxy Frontend
*/}}
{{- define "docspace.svc.proxyFrontend.create" -}}
{{- if empty .Values.proxyFrontend.service.existing }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the service name for DocSpace Proxy Frontend
*/}}
{{- define "docspace.svc.proxyFrontend.name" -}}
{{- if .Values.proxyFrontend.service.existing -}}
    {{- printf "%s" (tpl .Values.proxyFrontend.service.existing $) -}}
{{- else -}}
    {{- printf "proxy-frontend" -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for DocSpace Data
*/}}
{{- define "docspace.pvc.data.name" -}}
{{- if .Values.persistence.docspaceData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.docspaceData.existingClaim $) -}}
{{- else }}
    {{- printf "docspace-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for DocSpace Data
*/}}
{{- define "docspace.pvc.data.create" -}}
{{- if empty .Values.persistence.docspaceData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for DocSpace People
*/}}
{{- define "docspace.pvc.people.name" -}}
{{- if .Values.persistence.peopleData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.peopleData.existingClaim $) -}}
{{- else }}
    {{- printf "people-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for DocSpace People
*/}}
{{- define "docspace.pvc.people.create" -}}
{{- if empty .Values.persistence.peopleData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for DocSpace Files
*/}}
{{- define "docspace.pvc.files.name" -}}
{{- if .Values.persistence.filesData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.filesData.existingClaim $) -}}
{{- else }}
    {{- printf "files-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for DocSpace Files
*/}}
{{- define "docspace.pvc.files.create" -}}
{{- if empty .Values.persistence.filesData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for DocSpace Router log
*/}}
{{- define "docspace.pvc.router.name" -}}
{{- if .Values.persistence.routerLog.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.routerLog.existingClaim $) -}}
{{- else }}
    {{- printf "router-log" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for DocSpace Router log
*/}}
{{- define "docspace.pvc.router.create" -}}
{{- if empty .Values.persistence.routerLog.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}


{{- define "docspace.langflow.databaseUrl" -}}
  {{- $password := . -}}
  {{- printf "postgresql://langflow:%s@pgvector:5432/langflow" $password -}}
{{- end -}}


{{/*
Return true if a secret object should be created for Langflow
*/}}
{{- define "docspace.langflow.createSecret" -}}
{{- if empty .Values.langflow.secret.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{- define "docspace.langflow.secretName" -}}
  {{- if .Values.langflow.secret.existingSecret -}}
    {{- printf "%s" (tpl .Values.langflow.secret.existingSecret $) -}}
  {{- else -}}
    {{- "docspace-langflow" -}}
  {{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for pgvector
*/}}
{{- define "docspace.pgvector.createSecret" -}}
{{- if empty .Values.pgvector.secret.existingSecret }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{- define "docspace.pgvector.secretName" -}}
  {{- if .Values.pgvector.secret.existingSecret -}}
    {{- printf "%s" (tpl .Values.pgvector.secret.existingSecret $) -}}
  {{- else -}}
    {{- "docspace-pgvector" -}}
  {{- end -}}
{{- end -}}

{{/*
Generate a random 512-bit secret if the secret does not already exist
*/}}
{{- define "docspace.generateSecret" -}}
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

{{- define "docspace.langflow.backendURL" -}}
    {{- printf "http://%s:%v" .Values.connections.langflowBackendHost  .Values.langflow.backend.containerPorts.backend -}}
{{- end -}}

{{- define "docspace.pgvector.password" -}}
{{- $secretName := "docspace-pgvector" -}}
{{- $secretKey := "POSTGRES_PASSWORD" -}}
{{- $existingSecret := (lookup "v1" "Secret" .Release.Namespace $secretName).data -}}
{{- if $existingSecret -}}
    {{- get $existingSecret $secretKey | b64dec -}}
{{- else -}}
    {{- randAlphaNum 64 -}}
{{- end -}}
{{- end -}}
