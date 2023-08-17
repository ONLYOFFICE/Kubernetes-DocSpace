# Changelog

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
