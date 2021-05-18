from bs4 import BeautifulSoup
import nltk 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import os
import codecs
import math
import sys
from collections import defaultdict
try:
    stop_words = stopwords.words('english')
    word_tokenize('test')
    
except:
    nltk.download('stopwords')
    nltk.download('punkt')
    stop_words = stopwords.words('english')

doc_id = 0

def cosine_magnitude(freq_list):
    magnitude = 0
    for i in freq_list.values():
        magnitude += i * i
    return math.sqrt(magnitude)

length_of_doc = lambda freq_list:len(freq_list.keys())

def posting_list_generator(DIR, stop_words, ps, docf):
    global doc_id
    print(f'Processing files: directory --> {DIR.name}. This will take some time. Please wait...')
    posting_list = defaultdict(list)
    for file in os.listdir(DIR):
        with codecs.open(os.path.join(DIR , file), 'r', encoding='utf-8', errors='ignore') as f:
            try:
                soup = BeautifulSoup(f.read(), 'html.parser')
                text = soup.body.text.lower()
                tokens = word_tokenize(text)
                stem_list =  [ps.stem(token) for token in tokens if token.isalpha() and token not in stop_words]
                freq_list = nltk.FreqDist(stem_list)
                docf.write(f"{doc_id},{DIR.name}/{file},{length_of_doc(freq_list)},{cosine_magnitude(freq_list)}\n")
                for word in freq_list:
                    posting_list[word].append((doc_id, freq_list[word]))
            except Exception as e:
                continue
        doc_id += 1
    return posting_list


def write_index_files(file1, file2, posting_list):
    with open(file1, 'w') as f1, open(file2, 'w') as f2:
        for item in sorted(posting_list.keys()):
            entry = []
            for doc_id, freq in posting_list[item]:
                entry.extend([str(doc_id), str(freq)])
            f1.write(f"{item},{f2.tell()}\n")
            f2.write(f"{len(posting_list[item])},{','.join(entry)}\n")


def index_merger(term_file_list, posting_file_list):
    merged_posting_list = defaultdict(lambda :[[0],[]])
    for idx, termfile in enumerate(term_file_list):
        with open(termfile, 'r') as f1, open(posting_file_list[idx], 'r') as f2:
            for line in f1.readlines():
                key, offset = line.split(',')
                offset = int(offset.strip())
                f2.seek(offset)
                posting = f2.readline().strip()
                posting_list = posting.split(',')
                merged_posting_list[key][0][0] += int(posting_list[0])
                merged_posting_list[key][1].extend(posting_list[1:])
    with open('inverted_index_terms.txt', 'w') as of1, open('inverted_index_postings.txt', 'w') as of2:
        for key in sorted(merged_posting_list.keys()):
            of1.write(f"{key},{of2.tell()}\n")
#             print(merged_posting_list[key][0], len(merged_posting_list[key][1]))
            of2.write(f"{','.join([str(merged_posting_list[key][0][0])] + merged_posting_list[key][1])}\n")
            

def boolean_retriever(query_stem_list):
    list_of_filelist = []
    result_set = set()
    with open('inverted_index_terms.txt', 'r') as f1, open('inverted_index_postings.txt') as f2:
        for line in f1.readlines():
            key, offset = line.split(',')
            if key in query_stem_list:
                f2.seek(int(offset))
                line = f2.readline()
                posting_list = line.split(',')
                file_list = [posting_list[i] for i in range(1, len(posting_list), 2)]
                list_of_filelist.append(file_list)
        if list_of_filelist:
            result_set = set(list_of_filelist[0])
            for fl in list_of_filelist[1:]:
                result_set.intersection_update(set(fl))

    if result_set:
        print('The list of files containing all tokens in the given query are:')
        with open('docInfo.txt', 'r') as df:
            for line in df.readlines():
                if line.split(',')[0] in result_set:
                    print(line.split(',')[1])
    else:
        print('No result found')

def main_menu():
    print("""Menu:
    1. Create Inverted Index files
    2. Query Retrieval
    Enter your choice: """)
    ch = int(input())
    return ch

if __name__ == '__main__':
    repeat = True
    while(repeat):
        ch = main_menu()
        if ch == 1:
            print('Note: Text file preprocessing and index creation consumes much time. \nAre you sure you want to perform indexing again and overwrite existing files?(y/N)')
            inner_repeat = True
            while(inner_repeat):
                ch1 = input()
                if ch1.lower() == 'y':
                    DIR  = input('Enter directory: ')
                    if not os.path.isdir(DIR):
                        print(f"Invalid Directory {DIR}")
                        sys.exit()
                    ps = PorterStemmer()
                    docf = open('docInfo.txt', 'w')
                    for item in os.scandir(DIR):
                        if item.is_dir():
                            postingfile_name = f"index_{item.name}_postings.txt"
                            indexfile_name = f"index_{item.name}_terms.txt"
                            posting_list = posting_list_generator(item, stop_words, ps, docf)
                            write_index_files(indexfile_name, postingfile_name, posting_list)
                    index_merger(['index_1_terms.txt', 'index_2_terms.txt', 'index_3_terms.txt'],
                            ['index_1_postings.txt', 'index_2_postings.txt', 'index_3_postings.txt'])
                    docf.close()
                    inner_repeat = False
                elif ch1.lower() == 'n':
                    inner_repeat = False
                else: 
                    print('\nWrong Option. Re-enter!\n')
                    
            repeat = False
                
        #Boolean Retrieval
        elif ch == 2:
            flag = True
            necessary_file_list = ['inverted_index_terms.txt', 'inverted_index_postings.txt', 'docInfo.txt']
            for fn in necessary_file_list:
                if not os.path.exists(fn):
                    flag = False
                    print('Index files are missing. Rerun and create index files first.')
            if flag:
                ps = PorterStemmer()
                query = input("Enter query: ").lower()
                tokens = word_tokenize(query)
                stem_list =  [ps.stem(token) for token in tokens if token.isalpha() and token not in stop_words]
                boolean_retriever(stem_list)
            print('Do you want to continue(y/N)')
            ch2 = input()
            print()
            if ch2.lower() != 'y':
                repeat = False
        else:
            print('\nWrong Option!\n')