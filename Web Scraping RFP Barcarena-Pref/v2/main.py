from bs4 import BeautifulSoup
import requests
import argparse
import csv
import concurrent.futures
import os
import sys
import shutil 
import logging

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


def write_table(table, filename, head_url, mode):
    if os.path.exists(filename):        
        e = Exception('this scraping seems to have been done already. Aborting overwrite.')
        logger.error(e)
        raise e
    
    my_log("writing to main table")
    
    with open(filename, mode, encoding='utf-8') as f:
        writer = csv.writer(f)
        heads = table.find('tr').findAll('th')
        heads = [head.get_text().replace('\n', "") for head in heads]
        writer.writerow(heads)
        for tr in table.findAll('tr')[0:]:
            row  = []
            cells = tr.findAll(['td'])
            for data in cells:
                if not data.find('a'):
                    row.append(data.get_text().replace('\n', ""))
                else:
                    row.append(', '.join(list(map(lambda x:head_url + x['href'],data.findAll('a')))))
            # for links in tr.findAll('a'):
            #     row.append(head_url + links['href'])
            if row:
                writer.writerow(row)
            
    my_log("writing to main table successful")


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
    name = os.path.join(directory, scrapename)
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
    soup = prepare_soup(url)
    main_table = soup.find('table')
    head_url = 'http://www.governotransparente.com.br'
    if main_table is None:
        my_log('No table found. Check on the link, it might have expired')
        sys.exit()
    write_table(main_table, filename, head_url, 'w+')