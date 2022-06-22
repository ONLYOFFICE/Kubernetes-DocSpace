Get the update strategy type for oform-config
*/}}
{{- define "appserver.update.strategyType" -}}
{{- if eq .Values.deploymetsUpdateStrategy.type "RollingUpdate" -}}
    {{- toYaml .Values.deploymetsUpdateStrategy | nindent 4 -}}
{{- else }}
    {{- omit .Values.deploymetsUpdateStrategy "rollingUpdate" | toYaml | nindent 4 -}}
{{- end -}}
{{- end -}}
