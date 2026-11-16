# Mock schemas

Files in this directory were created using the following command:

```bash
docker run --rm -e PGPASSWORD=<password> postgres:17 pg_dump -d openledger -h <url> -p 5432 -U deploy -t 'public.<table>' --schema-only
```
