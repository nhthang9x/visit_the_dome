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
        self.list_party = ['liberal', 'progressive conservative', 'conservative (1867-1942)', 'new democratic party',
                           'conservative', 'co-operative commonwealth federation (c.c.f.)', 'bloc québécois',
                           'social credit', 'unionist', 'national government', 'reform', 'laurier liberal',
                           'independent', 'progressive', 'canadian alliance', 'ralliement créditiste',
                           'liberal-conservative', 'united farmers of alberta', 'labour', 'no affiliation',
                           'liberal labour', 'unionist (liberal)', 'independent conservative', 'liberal progressive',
                           'independent liberal', 'green', 'ndp', 'independent progressive', 'green party',
                           'independent progressive conservative', 'independent labour', 'nationalist liberal',
                           'reconstruction', 'independent c.c.f.', 'bloc populaire canadien',
                           'united farmers of ontario-labour', 'united farmers', 'unity', 'new party', 'bloc',
                           'labour progressive', 'new democracy', 'united farmers of ontario', 'gpq (ex-bloc)',
                           'forces et démocratie', 'québec debout', 'nationalist']
        # Statistic for entire dataset
        self.goverment_count = 0
        self.opposite_count = 0
        self.unknown_count = 0
        self.total_count_before = 0
        self.total_count_after = 0

        # self.read_through(data_path=data_path)
        # for idx, item in enumerate(self.list_path):
        #     print("{}: {}".format(idx, item))

        # self.copy_folders_without_files(input=data_path)
        # self.list_path_new = ["result/{}".format(str(os.path.relpath(str(path)[8:]))) for path in self.list_path]
        self.party_duration = pd.read_csv(filepath_or_buffer='data/PartyData.csv', header=0, delimiter=';').values
        #
        # for path in self.list_path_new:
        #     self.create_csv(input_file=path)

        # for idx, input_path in enumerate(self.list_path):
        #     self.count_total_row(input_file=input_path)

        # for idx, input_path in enumerate(self.list_path_new):
        #     _ = self.add_role_process(input_file=self.list_path[idx], output_file=input_path)

        self.create_csv(input_file='result/labeled_oral_questions.csv')
        self.create_csv(input_file='result/labeled_statements_by_members.csv')
        self.OQ_result = self.add_role_process(input_file='data/unduplicated_oral_questions.csv',
                                               output_file='result/labeled_oral_questions.csv')
        self.STM_result = self.add_role_process(input_file='data/unduplicated_statements_by_members.csv',
                                                output_file='result/labeled_statements_by_members.csv')

        # for input_path in self.list_path_new:
        #     self.remove_duplicated_words(source_file=input_path, new_file=input_path)
        #     self.count_total_row(input_file=input_path)
        # print("Total of row before remove duplicated row: {}".format(self.total_count_before))
        # print("Total of row after remove duplicated row: {}".format(self.total_count_after))
        # print("The number of Government record: {}".format(self.goverment_count))
        # print("The number of Opposite record: {}".format(self.opposite_count))
        # print("The number of Unknown record: {}".format(self.unknown_count))

        # for input_path in self.list_path:
        #     self.remove_duplicated_words(source_file=input_path,new_file=input_path)
        self.summary_report(file_name='result/summary.txt')

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
        government_count = 0
        opposite_count = 0
        unknown_count = 0
        input_csv = pd.read_csv(filepath_or_buffer=input_file, header=0).values
        with open(file=output_file, mode='a', encoding="utf-8") as output_csv:
            output_writer = csv.writer(output_csv)
            speech_time = parser.parse(input_csv[0, 2])
            print(speech_time)
            for speech_record in input_csv:
                self.total_count_before += 1
                for row in self.party_duration:
                    if (speech_time > parser.parse(str(row[0]))) and (speech_time < parser.parse(str(row[1]))):
                        if str(speech_record[11]).lower() in str(row[2]).lower():
                            government_count += 1
                            text = ["Government"]
                        else:
                            if str(speech_record[11]).lower() in self.list_party:
                                opposite_count += 1
                                text = ["Opposite"]
                            else:
                                unknown_count += 1
                                text = ["Unknown"]
                        text.extend(['{}'.format(str(column)) for column in speech_record])
                        output_writer.writerow(text)
                        break
            output_csv.close()
        return [government_count, opposite_count, unknown_count]

    def count_total_row(self, input_file):
        input_csv = pd.read_csv(filepath_or_buffer=input_file, header=0).values
        for row in input_csv:
            self.total_count_after += 1
            if str(row[0]) == "Government":
                self.goverment_count += 1
            elif str(row[0]) == "Opposite":
                self.opposite_count += 1
            else:
                self.unknown_count += 1
            # print(self.total_count)

    def remove_duplicated_words(self, source_file='result/oral_questions.csv', keep_record="first",
                                new_file='result/unduplicated_oral_questions.csv'):
        df = pd.read_csv(filepath_or_buffer=source_file, header=0)
        df.drop_duplicates(inplace=True, subset='speechtext', keep=keep_record)
        df.to_csv(new_file, index=False)

    def summary_report(self, file_name):
        with open(file=file_name, mode='a', encoding="utf-8") as text_file:
            # text_file.write("\n The total row of entire dataset before removing duplicated data: {} \n".format(
            #     self.total_count_before))
            # text_file.write("\n The total row of entire dataset after removing duplicated data: {} \n".format(
            #     self.total_count_after))
            #
            # text_file.write("\n In Entire Dataset \n")
            # text_file.write("\n Government row: {} \n".format(self.goverment_count))
            # text_file.write("\n Opposite row: {} \n".format(self.opposite_count))
            # text_file.write("\n Unknown row: {} \n".format(self.unknown_count))

            text_file.write("\n In Oral_Questions \n")
            text_file.write("\n Government row: {} \n".format(self.OQ_result[0]))
            text_file.write("\n Opposite row: {} \n".format(self.OQ_result[1]))
            text_file.write("\n Unknown row: {} \n".format(self.OQ_result[2]))

            text_file.write("\n In Statement By Member \n")
            text_file.write("\n Government row: {} \n".format(self.STM_result[0]))
            text_file.write("\n Opposite row: {} \n".format(self.STM_result[1]))
            text_file.write("\n Unknown row: {} \n".format(self.STM_result[2]))


if __name__ == '__main__':
    Preprocessing(data_path="../data/lipad")
