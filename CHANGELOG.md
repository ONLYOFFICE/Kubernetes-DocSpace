# Changelog

## 3.0.1

### Changes

* Released ONLYOFFICE DocSpace v3.0.1

## 3.0.0

### New Features

* Added OAuth2.0 service
* Added [Helm Docs](https://github.com/ONLYOFFICE/Kubernetes-Docs/tree/master) Subchart

### Changes

* Released ONLYOFFICE DocSpace v3.0.0
* Docker version of the Docs for DocSpace has been changed with Kubernetes Docs version

## 2.4.1

### Changes

* Released ONLYOFFICE DocSpace v2.6.3

## 2.4.0

### New Features

* Added the ability to run rootless containers

### Changes

* Released ONLYOFFICE DocSpace v2.6.2

## 2.3.0

### New Features

* Added the ability to set up container `lifecycle` hooks

### Changes

* Released ONLYOFFICE DocSpace v2.6.0
* Various images of service containers have been replaced with one already configured image with utils

### Fixes

* Fixed MySQL 8.4 startup error

## 2.2.0

### New Features

* Added the ability set up `annotations` for all the deployed resources
* Added the ability to set up its own `podAnnotations` for each service or define them globally

### Changes

* Released v2.5.1 of ONLYOFFICE DocSpace

## 2.1.0

### New Features

* Added the ability to set up `kind` for services. By default, `Deployment`
* Added the ability to choose which services to deploy
* Added the ability to set up its own `podSecurityContext` and `containerSecurityContext` for each service or define them globally 
* Added the ability to set up custom `podAntiAffinity`
* Added the ability to set up its own `nodeSelector` and `tolerations` for each service or define them globally

### Changes

* Released v2.5.0 of ONLYOFFICE DocSpace
* Using an already configured image for the `helm test` command
* Replaced ElasticSearch with OpenSearch
* Removed ipv6 disabling for localhost in router

## 2.0.3

### Changes

* Released v2.0.3 of ONLYOFFICE DocSpace

## 2.0.2

### Changes

* Released v2.0.2 of ONLYOFFICE DocSpace

## 2.0.1

### Changes

* Updated the Security Context Constraints policy for OpenShift

## 2.0.0

### New Features

* Added the ability set up custom Init Containers
* Added an Init Container that checks the availability of the database
* Added `helm test` for DocSpace launch testing and connected dependencies availability testing
* Added `NOTES.txt`

### Changes

* Released v2.0.0 of ONLYOFFICE DocSpace

## 1.2.0

### New Features

* Uses OpenResty as a routing service

### Changes

* Changes the name of the routing service

### Fixes

* Fixed services run errors

## 1.1.0

### New Features

* Added Healthchecks service
* Added the ability set up custom `labels`, `nodeAffinity`, `podAffinity` and `namespace`
* Added the ability to specify an existing `ServiceAccount` or create a new one
* Automated installation of Elasticsearch
* Added the ability to specify existing Secrets

### Changes

* Changes have been made to the installation of dependencies
* Released v1.1.1 of ONLYOFFICE DocSpace

### Fixes

* Fixed Ingress Class definition
* Fixed errors in the run of Init Containers
* Fixed `selector` for deployment services
* Fixed the path for the license in the local ONLYOFFICE Docs
* Fixed proxy error when connecting an external ONLYOFFICE Docs

## 1.0.0

* Initial release
