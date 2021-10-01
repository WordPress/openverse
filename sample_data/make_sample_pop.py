import csv
import random


in_tsv = open("sample_data.csv", "r")
out_tsv = open("sample_popularity_data.csv", "w+")
output_fields = ["identifier", "normalized_popularity"]
reader = csv.DictReader(in_tsv, delimiter=",")
writer = csv.DictWriter(out_tsv, delimiter=",", fieldnames=output_fields)
writer.writeheader()
for row in reader:
    pop = random.uniform(0, 100)
    out_row = {"identifier": row["identifier"], "normalized_popularity": pop}
    writer.writerow(out_row)
