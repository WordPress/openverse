import csv
from uuid import uuid4

with open('test_url_dump.csv', 'w') as csvfile, open('pagelist', 'r') as pages:
    writer = csv.DictWriter(csvfile, fieldnames=['url','identifier','provider'])
    writer.writeheader()
    for page in pages.readlines():
        page = page.rstrip()
        writer.writerow({'url': 'http://localhost:8080/' + page, 'identifier': str(uuid4()), 'provider': 'localhost'})
