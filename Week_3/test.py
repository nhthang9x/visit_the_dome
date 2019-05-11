import pandas as pd
from dateutil import parser
import csv

text = pd.read_csv(filepath_or_buffer='data/PartyTermData.csv', header=0, delimiter=',', usecols=[0]).values
# test =str(text[0])
# a = test.split("–")
# print(a[0])
# result = parser.parse(a[0])
# print(result)
with open(file="PartyData.csv", mode='a', encoding="utf-8") as csvfile:
    field = ["Begin Time", "End Time", "Government"]
    csv_file = csv.DictWriter(f=csvfile, fieldnames=field)
    csv_file.writeheader()
    # for duration in text:
    #     begin_time, end_time = str(duration[0]).split("–")
    #     begin_time = parser.parse(begin_time)
    #     end_time = parser.parse(end_time, t)
    #     print("{}-{}".format(begin_time,end_time))
    #     # csv_file.writerow()
csvfile.close()
