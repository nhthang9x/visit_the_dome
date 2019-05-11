from datetime import datetime
from dateutil import parser
import os
import shutil
import re
import csv
import pandas as pd


class Preprocessing():
    def __init__(self, data_path):
        super().__init__()
        if os.path.isdir('result'):
            shutil.rmtree('result')
        os.makedirs('result')
        self.list_path = []
        self.list_party = ['liberal', 'conservative', 'unionist coalition', 'national liberal and conservative',
                           'progressive conservative']
        # Statistic for entire dataset
        self.goverment_count = 0
        self.opposite_count = 0
        self.unknown_count = 0
        self.total_count = 0


        self.read_through(data_path=data_path)
        self.copy_folders_without_files(input=data_path)
        self.list_path_new = ["result/{}".format(str(os.path.relpath(str(path)[8:]))) for path in self.list_path]
        self.party_duration = pd.read_csv(filepath_or_buffer='data/PartyData.csv', header=0, delimiter=';').values
        # print(self.party_duration[0][0])

        for path in self.list_path_new:
            self.create_csv(input_file=path)

        for idx, input_path in enumerate(self.list_path):
            self.add_role_process(input_file=input_path, output_file=self.list_path_new[idx])
        print("The number of Government record: {}".format(self.goverment_count))
        print("The number of Opposite record: {}".format(self.opposite_count))
        print("The number of Unknown record: {}".format(self.unknown_count))

    def read_through(self, data_path):
        for root, directory, files in os.walk(data_path):
            for folder in directory:
                self.read_through(folder)
            for file in files:
                self.list_path.append(root + "/" + os.path.relpath(file))

    def create_csv(self, input_file):
        output_path = input_file.replace("\\", "/")
        with open(output_path, mode="a", encoding="utf-8") as csvfile:
            field = ["Role", "basepk", "hid", "speechdate", "pid", "opid", "speakeroldname", "speakerposition",
                     "maintopic",
                     "subtopic", "subsubtopic", "speechtext", "speakerparty", "speakerriding", "speakername",
                     "speakerurl"]
            csv_file = csv.DictWriter(f=csvfile, fieldnames=field)
            csv_file.writeheader()
        csvfile.close()

    def copy_folders_without_files(self, input):
        for folder in os.walk(input):
            path = 'result/{}'.format(str(folder[0])[8:])
            if not os.path.isdir(path):
                os.makedirs(path)

    def add_role_process(self, input_file, output_file):
        input_csv = pd.read_csv(filepath_or_buffer=input_file, header=0).values
        with open(file=output_file, mode='a', encoding="utf-8") as output_csv:
            output_writer = csv.writer(output_csv)
            speech_time = parser.parse(input_csv[0, 2])
            print(speech_time)
            for speech_record in input_csv:
                self.total_count += 1
                for row in self.party_duration:
                    if (speech_time > parser.parse(str(row[0]))) and (speech_time < parser.parse(str(row[1]))):
                        if str(speech_record[11]).lower() in str(row[2]).lower():
                            text = ["Government"]
                            self.goverment_count += 1
                        elif str(speech_record[11]).lower() in self.list_party:
                            text = ['Opposite']
                            self.opposite_count += 1
                        else:
                            text = ['Unknown']
                            self.unknown_count += 1
                        text.extend(['{}'.format(str(column)) for column in speech_record])
                        output_writer.writerow(text)
                        break


if __name__ == '__main__':
    Preprocessing(data_path="../data/lipad")
