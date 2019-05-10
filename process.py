import numpy as np
import pandas as pd
import os
import csv
import shutil
from nltk import word_tokenize, sent_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk import bigrams, trigrams
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string


class Preprocessing():
    def __init__(self, data_path):
        super().__init__()
        if os.path.isdir('result'):
            shutil.rmtree('result')
        os.makedirs('result')
        self.list_path = []
        self.read_through(data_path=data_path)
        self.stopwords = stopwords.words("english")

        # Task 1: Process all debates into two datasets: "Oral questions" and "Statements By Members"
        self.create_csv()
        self.write_csv()

        # Step 2: Remove duplicate rows in the two dataset if any
        self.remove_duplicated_words(source_file='result/oral_questions.csv',
                                     new_file='result/unduplicated_oral_questions.csv')
        self.remove_duplicated_words(source_file='result/statements_by_members.csv',
                                     new_file='result/unduplicated_statements_by_members.csv')

        self.frequent_word_OQ = []
        self.frequent_word_OQ.append(
            self.unique_word(csv_file="result/oral_questions.csv", record_file="result/OQ_10_most_occurring_words.csv"))
        self.frequent_word_OQ.append(self.unique_two_word(csv_file="result/oral_questions.csv",
                                                          record_file="result/OQ_10_most_occurring_two_words.csv"))
        self.frequent_word_OQ.append(self.unique_three_word(csv_file="result/oral_questions.csv",
                                                            record_file="result/OQ_10_most_occurring_three_words.csv"))

        self.frequent_word_SBM = []
        self.frequent_word_SBM.append(self.unique_word(csv_file="result/statements_by_members.csv",
                                                       record_file="result/SBM_10_most_occurring_words.csv"))
        self.frequent_word_SBM.append(self.unique_two_word(csv_file="result/statements_by_members.csv",
                                                           record_file="result/SBM_10_most_occurring_two_words.csv"))
        self.frequent_word_SBM.append(self.unique_three_word(csv_file="result/statements_by_members.csv",
                                                             record_file="result/SBM_10_most_occurring_three_words.csv"))

        # print("10 most occurring words: ", unique_one_words)
        # print("10 most occurring two sequential words: ", unique_two_words)
        # print("10 most occurring three sequential words: ", unique_three_words)

        self.summary_report(file_name='result/summary.txt')

    def read_through(self, data_path):
        for root, directory, files in os.walk(data_path):
            for folder in directory:
                self.read_through(folder)
            for file in files:
                self.list_path.append(root + "/" + os.path.relpath(file))

    def create_csv(self):
        if os.path.isfile("result/oral_questions.csv"):
            os.remove("result/oral_questions.csv")
        else:
            with open("result/oral_questions.csv", mode="a", encoding="utf-8") as csvfile:
                field = ["basepk", "hid", "speechdate", "pid", "opid", "speakeroldname", "speakerposition", "maintopic",
                         "subtopic", "subsubtopic", "speechtext", "speakerparty", "speakerriding", "speakername",
                         "speakerurl"]
                csv_file = csv.DictWriter(f=csvfile, fieldnames=field)
                csv_file.writeheader()
            csvfile.close()

        if os.path.isfile("result/statements_by_members.csv"):
            os.remove("result/statements_by_members.csv")
        else:
            with open("result/statements_by_members.csv", mode="a", encoding="utf-8") as csvfile:
                field = ["basepk", "hid", "speechdate", "pid", "opid", "speakeroldname", "speakerposition", "maintopic",
                         "subtopic", "subsubtopic", "speechtext", "speakerparty", "speakerriding", "speakername",
                         "speakerurl"]
                csv_file = csv.DictWriter(f=csvfile, fieldnames=field)
                csv_file.writeheader()
            csvfile.close()

    def write_csv(self):
        for file_path in self.list_path:
            data = pd.read_csv(filepath_or_buffer=file_path, header=0).values
            for row in data:
                if str(row[7]) == "Oral Questions":
                    with open("result/oral_questions.csv", mode="a", encoding="utf-8") as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(row)
                    csv_file.close()
                elif str(row[7]) == "Statements By Members":
                    with open("result/statements_by_members.csv", mode="a", encoding="utf-8") as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(row)
                    csv_file.close()
                else:
                    pass

    # Report 10 most occurring words
    def unique_word(self, csv_file, num_word=10, record_file="result/OQ_10_most_occurring_words.csv"):
        all_words = []
        unique_words = {}
        data_text = pd.read_csv(filepath_or_buffer=csv_file).values
        data_text = [str(record[10]).lower() for record in data_text]
        for record in data_text:
            for sent in sent_tokenize(text=record):
                for word in word_tokenize(text=sent):
                    if word not in self.stopwords:
                        all_words.append(word)

        # porter = PorterStemmer()
        # all_word = [porter.stem(word) for word in all_words]

        for word in all_words:
            if word in string.punctuation:
                continue
            if word not in unique_words.keys():
                unique_words[word] = 1
            else:
                unique_words[word] += 1

        self.record_words(path=record_file, list_words=unique_words)
        word_dict = sorted(unique_words, key=unique_words.get, reverse=True)[0:num_word]

        return word_dict

    # 10 most occurring two sequential words
    def unique_two_word(self, csv_file, num_word=10, record_file="result/OQ_10_most_occurring_two_words.csv"):
        data_text = pd.read_csv(filepath_or_buffer=csv_file).values
        data_text = [str(record[10]).lower() for record in data_text]

        tokenizer = RegexpTokenizer(r'\w+')
        data_text = [tokenizer.tokenize(record) for record in data_text]
        data_text = [[item for item in record if item not in self.stopwords] for record in data_text]
        data_text = [" ".join(record) for record in data_text]
        data_text = [bigrams(sequence=record.split()) for record in data_text]
        data_text = [["{} {}".format(item[0], item[1]) for item in record] for record in data_text]
        all_two_words = []
        unique_two_words = {}
        for record in data_text:
            for item in record:
                all_two_words.append(item)
        for item in all_two_words:
            if item not in unique_two_words.keys():
                unique_two_words[item] = 1
            else:
                unique_two_words[item] += 1

        self.record_words(path=record_file, list_words=unique_two_words)
        word_dict = sorted(unique_two_words, key=unique_two_words.get, reverse=True)[0:num_word]

        return word_dict

    # 10 most occurring two sequential words
    def unique_three_word(self, csv_file, num_word=10, record_file="result/OQ_10_most_occurring_three_words.csv"):
        data_text = pd.read_csv(filepath_or_buffer=csv_file).values
        data_text = [str(record[10]).lower() for record in data_text]

        tokenizer = RegexpTokenizer(r'\w+')
        data_text = [tokenizer.tokenize(record) for record in data_text]
        data_text = [[item for item in record if item not in self.stopwords] for record in data_text]
        data_text = [" ".join(record) for record in data_text]
        data_text = [trigrams(sequence=record.split()) for record in data_text]
        data_text = [["{} {} {}".format(item[0], item[1], item[2]) for item in record] for record in data_text]
        all_three_words = []
        unique_three_words = {}
        for record in data_text:
            for item in record:
                all_three_words.append(item)
        for item in all_three_words:
            if item not in unique_three_words.keys():
                unique_three_words[item] = 1
            else:
                unique_three_words[item] += 1

        self.record_words(path=record_file, list_words=unique_three_words)
        word_dict = sorted(unique_three_words, key=unique_three_words.get, reverse=True)[0:num_word]

        return word_dict

    def remove_duplicated_words(self, source_file='result/oral_questions.csv', keep_record="first",
                                new_file='result/unduplicated_oral_questions.csv'):
        df = pd.read_csv(filepath_or_buffer=source_file, header=0)
        df.drop_duplicates(inplace=True, subset='speechtext', keep=keep_record)
        df.to_csv(new_file, index=False)

    def record_words(self, path, list_words):
        with open(path, mode="a", encoding="utf-8") as csv_file:
            for w in sorted(list_words, key=list_words.get, reverse=True):
                row = "{}, {}".format(w, list_words[w])
                csv_file.write(row + "\n")
        csv_file.close()

    def summary_report(self, file_name):
        with open(file=file_name, mode='a', encoding="utf-8") as text_file:
            text_file.write("Summary of PreProcessing \n")
            # text_file.write("Data of Oral questions: {} \n".format(os.path.abspath(path='oral_questions.csv')))
            # text_file.write(
            #     "Data of Statements By Members: {} \n".format(os.path.abspath(path='statements_by_members.csv')))
            text_file.write("\n")
            text_file.write("In Oral_Questions \n")

            data_file = pd.read_csv(filepath_or_buffer='result/oral_questions.csv', header=0).values
            text_file.write("Before Removing duplicate rows, the number of row: {} \n".format(len(data_file)))

            data_file = pd.read_csv(filepath_or_buffer='result/unduplicated_oral_questions.csv', header=0).values
            text_file.write("After Removing duplicate rows, the number of row: {} \n".format(len(data_file)))

            text_file.write("\n")
            text_file.write("In Statements By Members \n")
            data_file = pd.read_csv(filepath_or_buffer='result/statements_by_members.csv', header=0).values
            text_file.write("Before Removing duplicate rows, the number of row: {} \n".format(len(data_file)))

            data_file = pd.read_csv(filepath_or_buffer='result/unduplicated_statements_by_members.csv', header=0).values
            text_file.write("After Removing duplicate rows, the number of row: {} \n \n".format(len(data_file)))

            text_file.write("10 most occurring words in Oral Questions \n")
            text_file.write('{} \n'.format(self.frequent_word_OQ[0]))

            text_file.write("10 most occurring two sequential words in Oral Questions \n")
            text_file.write('{} \n'.format(self.frequent_word_OQ[1]))

            text_file.write("10 most occurring three sequential words in Oral Questions \n")
            text_file.write('{} \n'.format(self.frequent_word_OQ[2]))

            text_file.write('\n')

            text_file.write("10 most occurring words in Statements By Members \n")
            text_file.write('{} \n'.format(self.frequent_word_SBM[0]))

            text_file.write("10 most occurring two sequential words in Statements By Members \n")
            text_file.write('{} \n'.format(self.frequent_word_SBM[1]))

            text_file.write("10 most occurring three sequential words in Statements By Members \n")
            text_file.write('{} \n'.format(self.frequent_word_SBM[2]))


if __name__ == '__main__':
    Preprocessing(data_path="../data/lipad")
