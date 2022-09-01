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
