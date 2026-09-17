# Migration to version 4.0.0

Starting from version 4.0.0 the chart is published as `onlyoffice/apps` (previously `onlyoffice/docspace`).
The old chart stays in the repository, but it is not updated anymore — if you keep using it, you will
not see version 4.0.0 and later.

Switching is a regular upgrade: the release name and all deployed resources stay the same, so there is
nothing to reinstall.

```bash
helm repo update
helm upgrade [RELEASE_NAME] -f values.yaml onlyoffice/apps
```

To check which chart your release currently uses:

```bash
helm list --namespace [NAMESPACE]
```

The `CHART` column shows `docspace-<version>` before the switch and `apps-<version>` after it.

## Notes

- The names of the deployed resources are not changed. Resources such as the `docspace-data` PVC, the
  `docspace-jwt` secret and the ConfigMaps keep their names, so the upgrade does not recreate them.
- The application images are renamed from `onlyoffice/docspace-*` to `onlyoffice/apps-*`. If you
  override `images.repoPrefix`, `images.registry` or any `Application.image.repository` parameter, update
  those values accordingly.
