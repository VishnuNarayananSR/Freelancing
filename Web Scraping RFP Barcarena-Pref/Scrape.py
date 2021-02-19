from bs4 import BeautifulSoup
import requests
import argparse
import csv
import concurrent.futures
import os
import sys
import shutil 

def prepare_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    try:
        print("preparing soup...")

        response =  requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        print("soup prepared...")
        
        return soup

    except Exception as e:
        print(f'Something went wrong...\n{e}') 
        sys.exit("Cannot proceed with this link further. exiting...") 


def write_table(table, filename, mode,):
    print("writing to main table")
    
    with open(filename, mode, encoding='utf-8') as f:
        writer = csv.writer(f)

        for tr in table.findAll('tr')[1:]:
            row  = []
            for data in tr.findAll(['th', 'td']):
                row.append(data.get_text().replace('\n', ""))
            writer.writerow(row)

    print("writing to main table successful")

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
    # print("writing to inner table")
    try:
        for tr in table.findAll('tr')[1:]:
            row  = []
            for data in tr.findAll(['td']):
                row.append(data.get_text())
            writer.writerow([val, url] + row)
        # print("writing to inner table successful")
    except AttributeError:
        print(f"Table(s) for entry {val} missing from url: {url}")
        
    

def thread_request(x):
    val, url = x
    response = requests.get(url)
    return (val, url, response)



def concurrent_response(arr, POOL_SIZE):
    with concurrent.futures.ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
        response_arr = executor.map(thread_request, [x for x in arr])
    response_arr = list(response_arr)
    return response_arr


def create_file(filename, table, mode = 'list'):
    extras = ["Cell value", "Link"]
    if mode == 'table':
        headings = list(map(lambda x: x.text, table.findAll('th')))
    else: 
        headings = ["List items"]
    with open(filename, "w+", encoding='utf-8') as file:
        w = csv.writer(file)
        w.writerow(extras + headings)


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, help='Name to csv file(s)')
    parser.add_argument('url', type=str, help='url of the page')
    parser.add_argument('--dir', type=str, help='name to the ouput directory', default='Ouput')
    parser.add_argument('--conn', type=int, help='number of concurrent connections. ideal value depends on your environment specifications', default=4)
    args = parser.parse_args()
    url = args.url
    name = args.name
    connections = args.conn
    directory = args.dir
    name = os.path.join(directory, name)
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        for file in os.listdir(directory):
            if file.endswith(".csv"):
                os.remove(os.path.join(directory, file)) 

    print(f"""
    Argument fetch successful

    name    :   {name}
    url     :   {url}
    
    """)

    return name,url, connections

def find_titles(soup, column):
    
    title_arr = list(map(lambda x:x.text, soup.findAll(['h2', 'h4'])))
    title_arr += list(map(lambda x:x.text, soup.findAll('strong')[1:]))
    titles = []
    for title in title_arr:
        titles.append("".join([i for i in title if i.isalpha()]))
    try:
        removable = ['DETALHEDALIQUIDAÇÃO', 'PREFEITURAMUNICIPALDEBARCARENAPA']
        titles = [i for i in titles if i not in removable]
    except:
        pass
    return titles

def output(response_arr, column):
    for val, url, response in response_arr:
        if response.status_code != 200:
            print(f'Bad response code {response.status_code}<----->{url}')
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        title_arr = find_titles(soup, column)
        container = soup.find_all('div', class_='row clearfix')[1:]
        elements = []
        for c in container:
            elements += c.find_all(["ul", "table"])
        # elements = container.find_all(["ul","table"])
        for i, element in enumerate(elements):
            title = title_arr[i]
            filename = f'{name}.{column}.{title.lower()}.csv'
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

if __name__ == '__main__':
    name, url, CONNECTIONS = get_arguments()
    # name = 'test'
    # url = 'http://www.governotransparente.com.br/transparencia/4382489/consultarliqdesporc/resultado?ano=8&inicio=01%2F01%2F2021&fim=24%2F01%2F2021&orgao=-1&elem=-1&unid=-1&valormax=&valormin=&credor=-1&clean=false'
    filename = name+'.csv'
    soup = prepare_soup(url)
    main_table = soup.find('table')
    write_table(main_table, filename, 'w+')
    head_url = 'http://www.governotransparente.com.br'
    empenho = []
    documento = []
    links = main_table.find_all('a')
    for link in links:
        category = link['href'].split('/')[3]
        if category == 'detalharempenhoportal':
            empenho.append((link.text, head_url + link['href']))
        else:
            documento.append((link.text, head_url+link['href']))


    print(f"""fetching requests for empenho...
    fetching {CONNECTIONS} requests at a time
    Tip: You can increase concurrent requests by using --conn parameter to speed up the process(check readme).
    """)
    response_arr = concurrent_response(empenho, CONNECTIONS)
    print("empenho fetch successful")
    output(response_arr, 'empenho')


    print(f"""fetching requests for documento...
    fetching {CONNECTIONS} requests at a time.
    """)
    response_arr = concurrent_response(documento, CONNECTIONS)
    print("documento fetch successful")
    output(response_arr, 'documento')








