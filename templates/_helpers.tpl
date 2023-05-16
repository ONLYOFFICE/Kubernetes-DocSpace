{{/*
Get the App Namespace
*/}}
{{- define "app.namespace" -}}
{{- if .Values.namespaceOverride -}}
    {{- .Values.namespaceOverride -}}
{{- else -}}
    {{- .Release.Namespace -}}
{{- end -}}
{{- end -}}

{{/*
Get the App labels
*/}}
{{- define "app.labels.commonLabels" -}}
{{- range $key, $value := .Values.commonLabels }}
{{ $key }}: {{ tpl $value $ }}
{{- end }}
{{- end -}}

{{/*
Get the App Service Account name
*/}}
{{- define "app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default .Release.Name .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Get the MySQL password secret
*/}}
{{- define "app.mysql.secretName" -}}
{{- if .Values.connections.mysqlPassword -}}
    {{- printf "%s-mysql" .Release.Name -}}
{{- else if .Values.connections.mysqlExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.mysqlExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for MySQL
*/}}
{{- define "app.mysql.createSecret" -}}
{{- if or .Values.connections.mysqlPassword .Values.connections.mysqlRootPassword (not .Values.connections.mysqlExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return MySQL password
*/}}
{{- define "app.mysql.password" -}}
{{- if not (empty .Values.connections.mysqlPassword) }}
    {{- .Values.connections.mysqlPassword }}
{{- else -}}
    {{- required "A MySQL Password is required!" .Values.connections.mysqlPassword }}
{{- end }}
{{- end -}}

{{/*
Return MySQL root password
*/}}
{{- define "app.mysql.rootPassword" -}}
{{- if not (empty .Values.connections.mysqlRootPassword) }}
    {{- .Values.connections.mysqlRootPassword }}
{{- else -}}
    {{- required "A MySQL root Password is required!" .Values.connections.mysqlRootPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Redis password secret
*/}}
{{- define "app.redis.secretName" -}}
{{- if or .Values.connections.redisPassword .Values.connections.redisNoPass -}}
    {{- printf "%s-redis" .Release.Name -}}
{{- else if .Values.connections.redisExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.redisExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Redis
*/}}
{{- define "app.redis.createSecret" -}}
{{- if or .Values.connections.redisPassword .Values.connections.redisNoPass (not .Values.connections.redisExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Redis password
*/}}
{{- define "app.redis.password" -}}
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
{{- define "app.broker.secretName" -}}
{{- if .Values.connections.brokerPassword -}}
    {{- printf "%s-broker" .Release.Name -}}
{{- else if .Values.connections.brokerExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.brokerExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for Broker
*/}}
{{- define "app.broker.createSecret" -}}
{{- if or .Values.connections.brokerPassword (not .Values.connections.brokerExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return Broker password
*/}}
{{- define "app.broker.password" -}}
{{- if not (empty .Values.connections.brokerPassword) }}
    {{- .Values.connections.brokerPassword }}
{{- else }}
    {{- required "A Broker Password is required!" .Values.connections.brokerPassword }}
{{- end }}
{{- end -}}

{{/*
Get the Broker URI
*/}}
{{- define "app.broker.uri" -}}
{{- $brokerSecret := include "app.broker.secretName" . }}
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
Return true if a service object should be created for App Proxy
*/}}
{{- define "app.svc.proxy.create" -}}
{{- if empty .Values.service.proxy.existing }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the service name for App Proxy
*/}}
{{- define "app.svc.proxy.name" -}}
{{- if .Values.service.proxy.existing -}}
    {{- printf "%s" (tpl .Values.service.proxy.existing $) -}}
{{- else -}}
    {{- printf "proxy" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a service object should be created for App Proxy Frontend
*/}}
{{- define "app.svc.proxyFrontend.create" -}}
{{- if empty .Values.proxyFrontend.service.existing }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the service name for App Proxy Frontend
*/}}
{{- define "app.svc.proxyFrontend.name" -}}
{{- if .Values.proxyFrontend.service.existing -}}
    {{- printf "%s" (tpl .Values.proxyFrontend.service.existing $) -}}
{{- else -}}
    {{- printf "proxy-frontend" -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for App Data
*/}}
{{- define "app.pvc.data.name" -}}
{{- if .Values.persistence.appData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.appData.existingClaim $) -}}
{{- else }}
    {{- printf "app-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for App Data
*/}}
{{- define "app.pvc.data.create" -}}
{{- if empty .Values.persistence.appData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for App People
*/}}
{{- define "app.pvc.people.name" -}}
{{- if .Values.persistence.peopleData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.peopleData.existingClaim $) -}}
{{- else }}
    {{- printf "people-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for App People
*/}}
{{- define "app.pvc.people.create" -}}
{{- if empty .Values.persistence.peopleData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for App Files
*/}}
{{- define "app.pvc.files.name" -}}
{{- if .Values.persistence.filesData.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.filesData.existingClaim $) -}}
{{- else }}
    {{- printf "files-data" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for App Files
*/}}
{{- define "app.pvc.files.create" -}}
{{- if empty .Values.persistence.filesData.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Get the PVC name for App Proxy log
*/}}
{{- define "app.pvc.proxy.name" -}}
{{- if .Values.persistence.proxyLog.existingClaim -}}
    {{- printf "%s" (tpl .Values.persistence.proxyLog.existingClaim $) -}}
{{- else }}
    {{- printf "proxy-log" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a pvc object should be created for App Proxy log
*/}}
{{- define "app.pvc.proxy.create" -}}
{{- if empty .Values.persistence.proxyLog.existingClaim }}
    {{- true -}}
{{- end -}}
{{- end -}}
