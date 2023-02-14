#!/bin/bash
APPSERVER_VERSION=""
APPSERVER_DEPLOYMENT=(onlyoffice-calendar onlyoffice-crm onlyoffice-files onlyoffice-mail onlyoffice-people-server onlyoffice-projects-server onlyoffice-proxy)
APPSERVER_STS=(onlyoffice-api onlyoffice-api-system onlyoffice-backup onlyoffice-files-services onlyoffice-notify onlyoffice-socket onlyoffice-storage-encryption onlyoffice-storage-migration onlyoffice-studio onlyoffice-studio-notify onlyoffice-telegram-service onlyoffice-thumbnails onlyoffice-urlshortener)

if [ "$1" == "" ]; then
  echo -e "\e[0;31m Basic parameters are missing. \e[0m"
  exit 1
else
  APPSERVER_VERSION=$1
fi

init_app_update_job(){
  kubectl get job | grep -iq app-update
  if [ $? -eq 0 ]; then
    echo -e "\e[0;31m A Job named app-update exists. Exit  \e[0m"
    exit 1
  else
    # wget https://raw.githubusercontent.com/ONLYOFFICE/server/master/schema/mysql/changedb.sql
    # kubectl create configmap change-db-scripts --from-file=./changedb.sql
    kubectl apply -f ./templates/configmaps/update-app.yaml
  fi
}

create_app_update_job(){
  kubectl apply -f ./templates/jobs/app-update.yaml
  sleep 5
  PODNAME="$(kubectl get pod | grep -i app-update | awk '{print $1}')"
}

check_app_update_pod_status(){
  while true; do
      STATUS="$(kubectl get pod "${PODNAME}" |  awk '{print $3}' | sed -n '$p')"
      case $STATUS in
          Error)
            echo "error"
            break
          ;;

          Completed)
            echo "completed"
            break
          ;;

          *)
            sleep 5
          ;;
      esac
  done
}

delete_app_update_job(){
  echo -e "\e[0;32m Status of the app-update POD: $POD_STATUS. The Job will be deleted. \e[0m"
  kubectl delete job app-update
}

update_images(){
  for sts in "${APPSERVER_STS[@]}"; do
     kubectl set image statefulset/$sts \
       $sts=onlyoffice/4testing-app-$(echo $sts | sed 's/[^-]*-//'):${APPSERVER_VERSION}
  done

  for deployment in "${APPSERVER_DEPLOYMENT[@]}"; do
    kubectl set image deployment/$deployment \
      $deployment=onlyoffice/4testing-app-$(echo $deployment | sed 's/[^-]*-//'):${APPSERVER_VERSION}
  done
}

print_error_message(){
  echo -e "\e[0;31m Status of the app-update POD: $POD_STATUS \e[0m"
  echo -e "\e[0;31m The Job will not be deleted automatically. Further actions to manage the Job must be performed manually. \e[0m"
}

init_app_update_job
create_app_update_job

echo "Getting the app-update POD status..."
POD_STATUS=$(check_app_update_pod_status)
if [[ "$POD_STATUS" == "error" ]]; then
  print_error_message
else
  delete_app_update_job
  update_images
  echo -e "\e[0;32m The Job update was completed successfully. Wait until all containers with the new version of the images have the READY status. \e[0m"
fi
exit
