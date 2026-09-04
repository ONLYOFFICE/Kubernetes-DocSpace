# Database migration to `onlyoffice_apps`

Starting from version 4.0.0 the default database name changed from `docspace` to `onlyoffice_apps`
(`connections.mysqlDatabase` and `docs.connections.dbName`). An existing installation keeps its data
in the old `docspace` database, so before upgrading you need to copy that data into `onlyoffice_apps`.

Only the MySQL database is copied. Files stored in the persistent volume are not affected — they are
addressed by tenant and file id, not by the database name, and keep working after the switch.

## Steps

Run the migration while the release is still on the previous version, then upgrade.

1. Copy the data with the provided job (adjust the values at the top of the file if your MySQL host,
   database names or root secret differ):

   ```bash
   kubectl apply -f sources/db-migration.yaml
   ```

2. Check the result — the table counts of both databases should match:

   ```bash
   kubectl logs job/docspace-db-migration
   ```

3. Upgrade to the new version (the default `onlyoffice_apps` is now populated):

   ```bash
   helm upgrade [RELEASE_NAME] -f values.yaml onlyoffice/docspace
   ```

4. Remove the job:

   ```bash
   kubectl delete -f sources/db-migration.yaml
   ```

## Notes

- The old `docspace` database is left untouched and can be kept as a backup or dropped later.
- The job connects as `root` (secret `mysql`, key `mysql-root-password`). For an external or
  managed MySQL, set the credentials to a user allowed to create the database, grant privileges and
  copy data.
- The image must provide `mysqldump`. If needed, set `image` to a MySQL client image matching your
  server version.
- To keep the new name but avoid the copy, set `connections.mysqlDatabase=docspace` and
  `docs.connections.dbName=docspace` on upgrade instead — the installation stays on the old database.

## Doing it manually

Instead of the job, the same result can be achieved by hand.

1. Get the MySQL root password:

   ```bash
   ROOT_PW=$(kubectl get secret mysql -o jsonpath='{.data.mysql-root-password}' | base64 -d)
   ```

2. Create the target database and grant access to the application user:

   ```bash
   kubectl exec mysql-0 -- mysql -u root -p"$ROOT_PW" \
     -e "CREATE DATABASE IF NOT EXISTS onlyoffice_apps; GRANT ALL PRIVILEGES ON onlyoffice_apps.* TO 'onlyoffice_user'@'%'; FLUSH PRIVILEGES;"
   ```

3. Copy the data from `docspace` to `onlyoffice_apps`:

   ```bash
   kubectl exec mysql-0 -- sh -c "mysqldump --single-transaction --routines --triggers -u root -p'$ROOT_PW' docspace" \
     | kubectl exec -i mysql-0 -- sh -c "mysql -u root -p'$ROOT_PW' onlyoffice_apps"
   ```
