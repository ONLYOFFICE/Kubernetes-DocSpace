Get the update strategy type for oform-config
*/}}
{{- define "appserver.update.strategyType" -}}
{{- if eq .Values.updateStrategy.type "RollingUpdate" -}}
    {{- toYaml .Values.updateStrategy | nindent 4 -}}
{{- else }}
    {{- omit .Values.updateStrategy "rollingUpdate" | toYaml | nindent 4 -}}
{{- end -}}
{{- end -}}
