Get the update strategy type for oform-config
*/}}
{{- define "appserver.update.strategyType" -}}
{{- if eq .Values.deploymetsUpdateStrategy.type "RollingUpdate" -}}
    {{- toYaml .Values.deploymetsUpdateStrategy | nindent 4 -}}
{{- else }}
    {{- omit .Values.deploymetsUpdateStrategy "rollingUpdate" | toYaml | nindent 4 -}}
{{- end -}}
{{- end -}}

{{/*
Get the MySQL password secret
*/}}
{{- define "appserver.mysql.secretName" -}}
{{- if .Values.connections.mysqlPassword -}}
    {{- printf "%s-mysql" .Release.Name -}}
{{- else if .Values.connections.mysqlExistingSecret -}}
    {{- printf "%s" (tpl .Values.connections.mysqlExistingSecret $) -}}
{{- end -}}
{{- end -}}

{{/*
Return true if a secret object should be created for MySQL
*/}}
{{- define "appserver.mysql.createSecret" -}}
{{- if or .Values.connections.mysqlPassword (not .Values.connections.mysqlExistingSecret) -}}
    {{- true -}}
{{- end -}}
{{- end -}}

{{/*
Return MySQL password
*/}}
{{- define "appserver.mysql.password" -}}
{{- if not (empty .Values.connections.mysqlPassword) }}
    {{- .Values.connections.mysqlPassword }}
{{- else }}
    {{- required "A MySQL Password is required!" .Values.connections.mysqlPassword }}
{{- end }}
{{- end -}}

{{/*
Return MySQL root password
*/}}
{{- define "appserver.mysql.rootPassword" -}}
{{- if not (empty .Values.connections.mysqlRootPassword) }}
    {{- .Values.connections.mysqlRootPassword }}
{{- else }}
    {{- required "A MySQL root Password is required!" .Values.connections.mysqlRootPassword }}
{{- end }}
{{- end -}}
