import argparse
import csv
import logging
import requests
import concurrent.futures
import os
from bs4 import BeautifulSoup
import sys
import time

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

def write_para(para, writer, val, link):
    links = para.findAll('a')
    links = ','.join([x['href'] for x in links])
    text = f"{para.get_text()} {' : ' + head_url + links}"
    writer.writerow([val, link] + [text])

def write_list(ul, writer, cell_val, link):
    string = []
    for li in ul.findAll('li'):
        child_divs = li.findChildren(["div"],recursive = True)
        if child_divs:
            string +=[div.text.replace("\n", "") for div in child_divs]
            continue
        string.append(li.text.replace("\n", ""))
    string = " | ".join(string)
    links = [x['href'] for x in li.findAll('a')]
    writer.writerow([cell_val, link, string] + links)


def write_inner_table(table, writer,val, url):
    # my_log("writing to inner table")
    try:
        for tr in table.findAll('tr')[1:]:
            row  = []
            for data in tr.findAll(['td']):
                links = data.findAll('a')
                if links:
                    links = ','.join([x['href'] for x in links])
                row.append(f"{data.get_text()} {(' : ' + head_url + links) if links else ''}")
            writer.writerow([val, url] + row)
        # my_log("writing to inner table successful")
    except AttributeError:
        my_log(f"Table(s) for entry {val} missing from url: {url}")


def thread_request(x):
    global DELAY
    val, url = x
    my_log(f'delaying for {DELAY}s...')
    time.sleep(DELAY)
    my_log(f'Fetching {val}, {url}')
    response = requests.get(url)
    return (val, url, response)


def concurrent_response(arr, POOL_SIZE):
    with concurrent.futures.ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
        response_arr = executor.map(thread_request, [x for x in arr])
    response_arr = list(response_arr)
    return response_arr


def create_file(filename, table, mode = 'list'):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    extras = ["Cell value", "Link"]
    if mode == 'table':
        headings = list(map(lambda x: x.text, table.findAll('th')))
    else: 
        headings = ["List items"]
    with open(filename, "w+", encoding='utf-8') as file:
        w = csv.writer(file)
        w.writerow(extras + headings)


def find_titles(soup, column):
    
    body = soup.find('div', 'body')
    title_arr = list(map(lambda x:x.text, body.findAll(['h2', 'h4', 'h5', 'strong'])))
#     title_arr = list(map(lambda x:x.text, body.findAll(['h2', 'h4'])))
#     title_arr += list(map(lambda x:x.text, body.findAll('strong')[1:]))
    titles = []
    for title in title_arr:
        titles.append("".join([i for i in title if i.isalpha()]))
    try:
        removable = ['DETALHEDALIQUIDAÇÃO', 'DETALHEDAANULAÇÃODALIQUIDAÇÃO', 'PREFEITURAMUNICIPALDEBARCARENAPA']
        titles = [i for i in titles if i not in removable]
    except:
        pass
    uniq_titles = []
    for i in titles:
        if i not in uniq_titles:
            uniq_titles.append(i)
    return uniq_titles


def output(response_arr, column):
    for val, url, response in response_arr:
        my_log(f'{val}, {url}')
        if response.status_code != 200:
            my_log(f'Bad response code {response.status_code}<----->{url}')
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        title_arr = find_titles(soup, column)
        container = soup.find_all('div', class_='row clearfix')[1:]
        elements = []
        for c in container:
            elements += c.find_all(["ul", "table", "p", "dl"])
        # elements = container.find_all(["ul","table"])
        for i, element in enumerate(elements):
            title = title_arr[i].lower()
            if title in ['itemdaliquidação','itensdaliquidação']:
                title = 'itensdanota'
            #filename = f'{directory}/{scrapename}/{column}/{title}/{stem}.csv'
            filename = f'{directory}/{scrapename}/{title}/{stem}.csv'
            if element.name == "table":
                if not os.path.exists(filename):
                    create_file(filename, element, mode='table')
                with open(filename, "a+", encoding='utf-8') as f:
                    w = csv.writer(f)
                    write_inner_table(element, w, val, url)
            elif element.name == "ul":
                if not os.path.exists(filename):
                    create_file(filename, element)
                with open(filename, "a+", encoding='utf-8') as f:
                    w = csv.writer(f)
                    write_list(element, w, val, url)
            elif element.name == 'p':
                if not os.path.exists(filename):
                    create_file(filename, element)
                with open(filename, "a+", encoding='utf-8') as f:
                    w = csv.writer(f)
                    write_para(element, w, val, url)
            elif element.name == 'dl':
                if not os.path.exists(filename):
                    create_file(filename, element)
                with open(filename, "a+", encoding='utf-8') as f:
                    w = csv.writer(f)
                    write_para(element, w, val, url)


if __name__ == '__main__':
    head_url = 'http://www.governotransparente.com.br'
    parser = argparse.ArgumentParser()
    parser.add_argument('scraping_name', type=str, help='Parent scraping name (such as consultarpagdesporc)')
    parser.add_argument('file_stem_name', type=str, help='CSV file base name (such as 2020-08)')
    parser.add_argument('--dir', type=str, help='name to the ouput directory', default='Output')
    parser.add_argument('--delay', type=int, help='delay between each request(in seconds)', default=0)
    parser.add_argument('--conn', type=int, help='number of concurrent connections. ideal value depends on your environment specifications', default=1)
    args = parser.parse_args()
    scrapename = args.scraping_name
    stem = args.file_stem_name   
    directory = args.dir
    CONNECTIONS = args.conn 
    global DELAY
    DELAY = args.delay
    print(f"""
    Argument fetch successful
    name            : {scrapename}
    file_stem_names : {stem}
    directory       : {directory}
    """)
    filename = f'{directory}/{scrapename}/main/{stem}.csv'
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit()
    logging.basicConfig(filename=f'{directory}/mainscrape.log', level=logging.DEBUG, 
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    logger.log(20, f'1Starting scraper to scrape {stem} of {scrapename}')
    logger.debug(f'2Starting scraper to scrape {stem} of {scrapename}')
    my_log(f'3Starting scraper to scrape {stem} of {scrapename}')
    empenho = []
    documento = []
    consultarcontratoaditivo = []
    links = []
    with open(filename,'r') as f:
        reader = csv.reader(f)
        # heads = list(reader)[0]
        for row in reader:
            for cell in row:
                if 'http' in cell:
                    links+=list(map(str.strip,(cell.split(','))))
            # documento.append((heads[-2], row[-2]))
            # empenho.append((heads[-1],row[-1]))
    for link in links:
        category = link.split('/')[5]
        if category == 'detalharempenhoportal':
            empenho.append(('empenho', link))
        elif category == 'consultarcontratoaditivo':
            consultarcontratoaditivo.append((category,link))
        else:
            documento.append((category, link))
    my_log('Tip: You can increase concurrent requests by using --conn parameter to speed up the process(check readme).')
    if scrapename != 'consultarempenho':
        my_log(f'skipping Empenho scraping for scrapename {scrapename}')
    else:
        my_log(f"""fetching requests for empenho...
        fetching {CONNECTIONS} requests at a time.""")
        response_arr = concurrent_response(empenho, CONNECTIONS)
        my_log("empenho fetch successful")
        output(response_arr, 'empenho')
        my_log('csv output successful.')

    my_log(f"""fetching requests for documento...
    fetching {CONNECTIONS} requests at a time.""")
    response_arr = concurrent_response(documento, CONNECTIONS)
    my_log("documento fetch successful")
    output(response_arr, 'documento')
    my_log('csv output successful.')

    my_log(f"""fetching requests for consultarcontratoaditivo...
    fetching {CONNECTIONS} requests at a time.""")
    response_arr = concurrent_response(consultarcontratoaditivo, CONNECTIONS)
    my_log("consultarcontratoaditivo fetch successful")
    output(response_arr, 'consultarcontratoaditivo')
    my_log('csv output successful.')

    my_log('Job done!')
