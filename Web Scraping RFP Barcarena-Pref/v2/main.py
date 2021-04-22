from bs4 import BeautifulSoup
import requests
import argparse
import csv
import concurrent.futures
import os
import sys
import shutil 
import logging
import pandas as pd
from datetime import datetime

log_type = 'log+print'
logger = None

def my_log(msg, level=10):
    """
    Level    Numeric value
    CRITICAL 50
    ERROR	 40
    WARNING	 30
    INFO	 20
    DEBUG	 10
    NOTSET	 0
    """
    #log_type = os.environ.get('log_type')
    assert log_type in ['print', 'log', 'log+print'], f"Invalid log type passed as env variable: {log_type}."
    if log_type == 'print' or 'log+print':
        print(msg)
    if log_type == 'log' or 'log+print':
        #logging.log(level, msg)
        logger.log(level, msg)


def return_table_df(table, head_url):
    
    # my_log("writing to main table")
    
    table = soup.find('table')
    heads = list(table.find('tr').stripped_strings)
    heads = heads[:-2] + [' '.join(heads[-2:])]
    rows = []
    for tr in table.findAll('tr')[1:]:
        row  = []
        cells = tr.findAll(['td'])
        for data in cells:
            if not data.find('a'):
                row.extend([i.replace("\n", "") for i in list(data.stripped_strings)])
            else:
                row.append(', '.join(list(map(lambda x:head_url + x['href'],data.findAll('a')))))
        rows.append(row)
    return pd.DataFrame(rows, columns = heads)
            
    # my_log("writing to main table successful")


def prepare_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    try:
        my_log("preparing soup...")

        response =  requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        my_log("soup prepared...")
        
        return soup

    except Exception as e:
        my_log(f'Something went wrong...\n{e}') 
        sys.exit("Cannot proceed with this link further. exiting...") 


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('scraping_name', type=str, help='Parent scraping name (such as consultarpagdesporc)')
    parser.add_argument('url', type=str, help='url of the page')
    parser.add_argument('file_stem_names', type=str, help='CSV file base name (such as 2020-08)')
    parser.add_argument('--dir', type=str, help='name to the output directory', default='Output')
    parser.add_argument('--conn', type=int, help='number of concurrent connections. ideal value depends on your environment specifications', default=4)
    args = parser.parse_args()
    url = args.url
    scrapename = args.scraping_name
    file_stem_names = args.file_stem_names
    connections = args.conn
    directory = args.dir
    #if not os.path.exists(directory):
    #    os.mkdir(directory)
    name = os.path.join(directory, scrapename, 'main') #, *(file_stem_names.split('/')[:-1])) #also if file_stem_names contains directories, add them
    if not os.path.exists(name):
        os.makedirs(name)
    #else:
    #    raise Exception(f'Directory {name} already exists. Choose a different one to avoid deleting.')
        #for file in os.listdir(directory):
        #    if file.endswith(".csv"):
        #        os.remove(os.path.join(directory, file)) 

    print(f"""
    Argument fetch successful
    name            : {name}
    file_stem_names : {file_stem_names}
    url             : {url}
    """)

    return directory, scrapename, name, file_stem_names, url, connections

def registry_log(scrapename, name, file_stem_names, rows_source, rows_scraped):
    if not os.path.exists(registry_file):
        with open(registry_file, 'w') as f:
            reg_writer = csv.writer(f)
            reg_writer.writerow(['Timestamp', 'Category', 'Subcategory', 'Title', 'Stem' , 'No of rows(Actual)', 'No of rows scraped'])
    timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    category = "DESPESAS GERAIS"
    subcategory = scrapename
    title = name.split('/')[-1]
    stem = file_stem_names
    with open(registry_file, 'a') as f:
        reg_writer = csv.writer(f)
        reg_writer.writerow([timestamp, category, subcategory, title, stem, rows_source, rows_scraped])

if __name__ == '__main__':
    directory, scrapename, name, file_stem_names, url, CONNECTIONS = get_arguments()
    logging.basicConfig(filename=f'{directory}/mainscrape.log', level=logging.DEBUG, 
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    logger.log(20, f'1Starting scraper to scrape {file_stem_names} of {scrapename}')
    logger.debug(f'2Starting scraper to scrape {file_stem_names} of {scrapename}')
    my_log(f'3Starting scraper to scrape {file_stem_names} of {scrapename}')

    # name = 'test'
    # url = 'http://www.governotransparente.com.br/transparencia/4382489/consultarliqdesporc/resultado?ano=8&inicio=01%2F01%2F2021&fim=24%2F01%2F2021&orgao=-1&elem=-1&unid=-1&valormax=&valormin=&credor=-1&clean=false'
    filename = f'{name}/{file_stem_names}.csv'
    registry_file = 'registry.csv'
    if os.path.exists(filename):        
        e = Exception('this scraping seems to have been done already. Aborting overwrite.')
        logger.error(e)
        raise e
    page = 1
    head_url = 'http://www.governotransparente.com.br'
    soup = prepare_soup(url)
    try:
        rows_source = soup.findAll('p')[-1].text.split()[-2]
    except:
        rows_source = None
    table = soup.find('table')
    df = return_table_df(table, head_url)
    max_pages = soup.find('div', 'pagination').input['data-max-page']
    while page < 6:#int(max_pages):
        page += 1
        print(f'scraping page{page}')
        soup = prepare_soup(f"{url}&page={page}")
        table = soup.find('table')
        df = df.append(return_table_df(table, head_url), ignore_index=True)

    df.to_csv(filename, index=False)
    rows_scraped = len(df.index)
    registry_log(scrapename, name, file_stem_names, rows_source, rows_scraped)