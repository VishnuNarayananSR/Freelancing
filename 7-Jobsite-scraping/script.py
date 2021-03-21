# from os import system

# system('pip install -r requirements.txt')

import datetime
import requests
import openpyxl
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def prepare_soup(link:str) -> BeautifulSoup:
    '''
    argument -- link:str
    return --   parsed HTML:BeautifulSoup if successful
                False:bool if failed
    '''
    html = requests.get(link)
    if html.status_code == 200:
        # open('a.txt','w',encoding='utf-8').write(html.text)
        return BeautifulSoup(html.text, "html.parser")
    else:
        return False

def filters():
    title = input("Enter job title to search for: ")
    location = input('Enter job location: ')
    postage = int(input("""Posted withtin:
    1. Last 24 hours
    2. Last 3 days
    3. Last 7 days
    4. Last 14 days
    0. All
 """))
    job_type = int(input("""Job Type:
    1. Permanent
    2. Contract
    3. Temporary
    4. Part Time
    0. All
"""))
    salary = int(input(""" Salary:
    1. at least £10,000 
    2. at least £20,000 
    3. at least £30,000 
    4. at least £40,000 
    5. at least £50,000 
    6. at least £60,000 
    7. at least £70,000 
    8. at least £80,000 
    9. at least £90,000 
    10. at least £100,000
    0. All
    """))
    N = int(input('Enter number of jobs to be scraped from each site:'))
    return title, location, postage, job_type, salary, N





def open_browser(driver, url):
    driver.get(url) 
    return driver




def click_on_filter(driver, element):
    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, element))
        )
    element.click()




def write_xl(df,filename, sheet):
    with pd.ExcelWriter(filename, engine="openpyxl", mode="a") as writer:
        df.to_excel(writer, sheet_name=sheet, index=False, encoding='utf-8')




# soup = None

def efc(driver, JOBTITLE, LOCATION): 

    def get_efc_descr(link):
        soup = prepare_soup(link)
        if not soup:
            return ''
        desc = soup.find_all('div',{'class':'jobContentFrame'})[0]
        summary = desc.text.strip()
        return summary


    age_dict = {0:'', 1 : "ONE", 2 : "THREE", 3 : "SEVEN", 4 : "SEVEN"}
    type_dict = ["CONTRACT", "PERMANENT","TEMPORARY", "INTERNSHIPS_AND_GRADUATE_TRAINEE"]
    type_dict.insert(0, '%7C'.join(type_dict))
    if sal_fltr < 4: sal = 'FIRST'
    elif sal_fltr < 8: sal = 'SECOND'
    else: sal = "THIRD_TIER|FOURTH_TIER|FIFTH_TIER|SIXTH"
    url = f'https://www.efinancialcareers.com/search/?q={JOBTITLE}&location={LOCATION}&page=1&pageSize=100&filters.postedDate={age_dict[age_fltr]}&filters.positionType={type_dict[jt_fltr]}&filters.salaryBand={sal}_TIER'
    print('fetching from site:', url)
    if age_fltr == 0: 
        url = url.replace('&filters.postedDate=','')
    driver = open_browser(driver, url)
    try:

        data = []
        count = 0
        next_btn = True
        while(count < N and next_btn is not None):
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/dhi-job-search/dhi-search-page-container/dhi-search-page/div/dhi-search-page-results/div/div[3]/js-search-display/div/div[2]/dhi-search-cards-widget/div/dhi-new-search-card[1]/div")))
            html = driver.page_source
            # global soup
            soup = BeautifulSoup(html, "html.parser")
            for job in soup.findAll('div', 'search-card'):
                if count >= N: 
                    break
                count += 1

                new_link = 'https://www.efinancialcareers.com/' + job.find_all('a',{'class':'card-title-link bold'})[0].attrs['href']
                summary = get_efc_descr(new_link)
                # summary = 'test'

                data.append([job.a.text.strip(),
                job.find('div', 'card-salary ng-star-inserted').text.strip(),
                job.find(id = 'searchResultLocation').text.strip(),
                job.find('span', {'data-cy' : 'card-posted-date'}).text.strip(),
                job.find('span', {'data-cy' : 'search-result-employment-type'}).text.strip(),
                summary
                # job.find('div', {'data-cy' : 'card-summary'}).text.strip() + '...'
                ])
            try:
                next_btn = None
                # next_btn = driver.find_element(By.XPATH, "/html/body/dhi-job-search/dhi-search-page-container/dhi-search-page/div/dhi-search-page-results/div/div[3]/js-search-display/div/div[3]/div[1]/js-search-pagination-container/pagination/ul/li[5]/a")
                next_btn = driver.find_elements_by_class_name('page-link')
                next_btn[-1].click()
            except NoSuchElementException:
                pass
            except Exception as e:
                print(e)
                break
    except TimeoutException:
        print('No search result found')
    except Exception as e:
        print('An error occured:', e)
    finally:
        df = pd.DataFrame(data, columns=['Job Title', 'Salary', 'Location', 'Post Date', 'Type', 'Intro'])
        write_xl(df, filename, 'efinancialcareeers')
        # driver.close()
        print('done')

def multi_site(driver, JOBTITLE, LOCATION, site = 'cw'):
    url_dict = {"cw":'https://www.cwjobs.co.uk',
        "total":"https://www.totaljobs.com",
        "jobsite": "https://www.jobsite.co.uk/",
        "city": "https://www.cityjobs.com/"
        }
    sal_element = f'//*[@id="facetListAnnualPayRate"]/ul/li[{sal_fltr}]/a'
    age_element = f'//*[@id="facetListDatePosted"]/div[2]/ul/li[{age_fltr}]/a'
    jt_element = f'//*[@id="facetListJobType"]/div[2]/ul/li[{jt_fltr}]/a'
    url = url_dict[site]
    print('fetching from site:', url)
    open_browser(driver, url)
    try:
        cookie = driver.find_element_by_class_name("privacy-prompt-button.primary-button.accept-button-new")
        cookie.click()
    except:
        pass
    title_field = driver.find_element_by_id("keywords")
    title_field.send_keys(JOBTITLE)
    loc_field = driver.find_element_by_id("location")
    loc_field.send_keys(LOCATION)
    search_btn = driver.find_element_by_id("search-button")
    search_btn.click()
    try: 
        data = []
        count = 0
        next_btn = True
        while(count < N and next_btn is not None):
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-9.job-results"))
            )
            if sal_fltr != 0:
                click_on_filter(driver, sal_element)
            if age_fltr != 0:
                click_on_filter(driver, age_element)
            if jt_fltr != 0:
                click_on_filter(driver, jt_element)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            link_ct = 0
            for job in soup.find_all('div', 'job'):
                link_ct += 1
                if not "ci-advert-job" in job['class']:
                    if count >= N: 
                        break
                    count += 1
                    try:
                        links = driver.find_elements_by_class_name('job-title')
                        data.append([job.find('h2').text,
                        job.find('li', 'salary').text,
                        job.find('li', 'location').span.text.replace('\n', ''),
                        job.find('li', 'date-posted').span.text.strip(),
                        job.find('li', 'job-type').span.text])
                    except:
                        print('Some jobs in this site have incomplete information to scrape. Skipping those...')
                    # job.find('p', 'job-intro').text])
                    try:
                        link = links[count].find_element_by_tag_name('a')
                        main_window = driver.current_window_handle
                        action = ActionChains(driver)
        
                        action.key_down(Keys.CONTROL).key_down(Keys.SHIFT).click(link).key_up(Keys.CONTROL).key_up(Keys.SHIFT).perform()

                        driver.switch_to.window(driver.window_handles[-1])
                        element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-description")))
                        desc = driver.page_source
                        desc = BeautifulSoup(desc, "html.parser")
                        p = desc.find('div', "job-description").text.strip()

                        data[-1].append(p)
                        # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
                        driver.close()
                        driver.switch_to.window(main_window)
                    except Exception as e:
                        print(e)
            try:
                link_ct = 0
                next_btn = None
                next_btn = driver.find_element_by_class_name('btn.btn-default.next')
                next_btn.click()
            except NoSuchElementException:
                pass
    except TimeoutException:
        print('No search result found')
    except Exception as e:
        print("An error occured: ",e)

    finally:
        print('done')
        df = pd.DataFrame(data, columns=['Job Title', 'Salary', 'Location', 'Post Date', 'Type', 'Intro'])
        write_xl(df, filename, site)
        # driver.close()


def indeed(driver, JOBTITLE, LOCATION):

    def indeed_job_description(link):
        soup = prepare_soup(link)
        if not soup:
            return ''
        summary = soup.find(id='jobDescriptionText').text.strip()
        return summary
    
    base_url = 'https://uk.indeed.com'

    type_list = ['','permanent','contract','temporary', 'parttime']
    age = {1:1,2:3,3:7,4:14,0:''}
    sal = sal_fltr*10000 if sal_fltr > 0 else ''
    url = f'https://uk.indeed.com/jobs?q={JOBTITLE}+£{sal}&l={LOCATION}&jt={type_list[jt_fltr]}&fromage={age[age_fltr]}'
    if jt_fltr == 0: 
        url = url.replace('&jt=', '')
    if age_fltr == 0: 
        url = url.replace('&fromage=', '')
    if sal_fltr == 0: 
        url = url.replace('+£','')
    print('fetching from site:', url)
    try:
        data = []
        count = 0
        next_btn = True
        while(count < N and next_btn is not None):
            open_browser(driver, url)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "resultsCol"))
            )
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            links = driver.find_elements_by_class_name('title')
            link_ct = 0
            for job in soup.findAll('div', 'jobsearch-SerpJobCard'):
                link_ct += 1
                if count >= N: 
                    break
                count += 1

                try:
                    salary = job.find_all('span',{'class':'salaryText'})[0].text.strip()
                except:
                    salary = '-NA-'
                # try:
                #     driver.find_element_by
                # except:
                #     intro = '-NA-'
                job_title = job.h2.a.text.strip()
                _location = job.find('span', 'location').text.strip()
                _date = job.find('span', 'date').text.strip()
                _type = type_list[jt_fltr]

                # click to new tab
                new_link = base_url + job.h2.a.attrs['href']
                _intro = indeed_job_description(new_link)

                data.append([job_title,
                salary,
                _location,
                _date,
                _type,
                _intro
                ])
                #click on job card
                # links[count].find_element_by_tag_name('a').click()
                driver.back()
            try:
                link_ct = 0
                next_btn = None
                next_btn = driver.find_element(By.XPATH, '//*[@id="resultsCol"]/nav/div/ul')
                pos = url.find('&start=')
                if pos != -1:
                    url = url[:pos]
                url = url + '&start='+str((count // 10) * 10)
            except NoSuchElementException:
                pass
    except TimeoutException:
        print('No search result found')
    except Exception as e:
        print('An error occured:', e)
    finally:
        df = pd.DataFrame(data, columns=['Job Title', 'Salary', 'Location', 'Post Date', 'Type', 'Intro'])
        write_xl(df, filename, 'indeed')
        # driver.close()
        print('done')

def format_filename(name):
    for i in set(name):
        if not i.isalnum():
            name = name.replace(i, '_')
    return name


if __name__ == '__main__':
    timestamp = str(datetime.datetime.now())
    filename = format_filename(timestamp) + '.xlsx'
    writer = openpyxl.Workbook()
    writer.save(filename)
    title, location, age_fltr, jt_fltr, sal_fltr, N = filters()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    multi_site(driver, title, location, site="cw")
    multi_site(driver, title, location, site="total")
    multi_site(driver, title, location, site="jobsite")
    multi_site(driver, title, location, site="city")
    efc(driver, title, location)
    indeed(driver, title, location)
    # Thread(target = efc("web-dev", "london")).start()
    # Thread(target = multi_site("web-dev", "london")).start()
    driver.quit()
