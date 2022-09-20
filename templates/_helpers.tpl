Get the update strategy type for App deploymets
*/}}
{{- define "app.update.strategyType" -}}
{{- if eq .Values.deploymetsUpdateStrategy.type "RollingUpdate" -}}
    {{- toYaml .Values.deploymetsUpdateStrategy | nindent 4 -}}
{{- else -}}
    {{- omit .Values.deploymetsUpdateStrategy "rollingUpdate" | toYaml | nindent 4 -}}
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
    {{- printf "onlyoffice-proxy" -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a service object should be created for App Proxy Frontend
*/}}
{{- define "app.svc.proxyFrontend.create" -}}
{{- if empty .Values.service.proxyFrontend.existing }}
    {{- true -}}
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
