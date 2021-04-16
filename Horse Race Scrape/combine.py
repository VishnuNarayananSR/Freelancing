import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time
from datetime import datetime
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
# import driver
from lxml import html
from webdriver_manager.chrome import ChromeDriverManager

curr = datetime.today().strftime('%Y-%m-%d %H-%M-%S')
today = datetime.today().strftime('%Y-%m-%d')

def find_xpath(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

OLBG_FILENAME = 'result '+today+'.csv'

def get_best_tip(driver, xpath):

    try:
        element = driver.find_element_by_xpath(xpath)
        driver.execute_script(f"""window.open("{element.get_attribute('href')}");""")
        driver.switch_to.window(driver.window_handles[1])
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "tips-content")))

        try:
            tree = html.fromstring(driver.page_source)
            odds = tree.xpath('//*[@id="tips-content"]/div[1]/div[3]/div/div[1]/div[2]/div[1]/div/span/text()')[0]
        except:
            odds = None
        try:
            tree = html.fromstring(driver.page_source)
            mp_tip_odds = tree.xpath('//*[@id="tips-content"]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div/span/text()')[0]
        except:
            mp_tip_odds = None
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            top_tip = soup.find('table', id='tipsListingContainer').findAll('tr', 'tip-row')[0]
        except:
            top_tip = None
        soup = soup.find('div', 'row row-eq-height')
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        print(e)
        print('page timed out', f"""window.open("{element.get_attribute('href')}");""")
    try:
        comment = soup.find('div', 'sport-tips-table-comments-text').text.strip().encode("ascii", "ignore").decode()
    except:
        comment = None
    
    try:
        best_tip_xprt_count = top_tip.find('div', 'experts-count').text.strip()
    except:
        best_tip_xprt_count = None
    try:
        form = top_tip.find('li','hr-details-placings').text.strip()
    except:
        form = None
    try:
        age = top_tip.find('li','hr-details-age').text.strip()
    except:
        age = None
    try:
        weight = top_tip.find('li','hr-details-weight').text.strip()
    except:
        weight = None
    try:
        trainer = top_tip.find('li','hr-details-trainer').text.strip()
    except:
        trainer = None
    try:
        jockey = top_tip.find('li','hr-details-jockey').text.strip()
    except:
        jockey = None
    tips_dict = {}
    try:
        tips_dict["win"] = top_tip.findAll('td','d-none d-lg-table-cell text-center')[0].find('p', 'tips').text.split(' ')[0]
    except:
        tips_dict["win"] = None
    try:
        tips_dict["ew"] = top_tip.findAll('td','d-none d-lg-table-cell text-center')[1].find('p', 'tips').text.split(' ')[0]
    except:
        tips_dict["ew"] = None
    try:
        tips_dict["naps"] = top_tip.findAll('td','d-none d-lg-table-cell text-center')[2].find('p', 'tips').text.split(' ')[0]
    except:
        tips_dict["naps"] = None
    try:
        mp_tip = soup.findAll('td', 'legend-selection-name')[0].text.strip()
    except:
        mp_tip = None
    try:
        tips = soup.findAll('td', 'legend-win-tips')[0].text.strip()
        n_mp_tips = tips.split('/')[0].strip()
        total_tips = tips.split('/')[1].strip()
    except:
        n_mp_tips = None
        total_tips = None
    try:
        tipster_name = soup.find('a', 'best-tipster-icon-header').text.strip()
    except:
        tipster_name = None
    try:
        type_ = soup.find('span', ['comment-type-label-win', 'comment-type-label-ew']).text.strip()
    except:
        type_ = None
    try:
        best_tipsters_tip = soup.findAll('h5', 'selection-name')[1].text.strip()
    except:
        best_tipsters_tip = None
    return((mp_tip, n_mp_tips, mp_tip_odds, total_tips, best_tipsters_tip, type_, tipster_name, odds, best_tip_xprt_count,
            form, age, weight, trainer, jockey, tips_dict, comment))



def scrape_olbg():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())


    driver.get('https://www.olbg.com/betting-tips/Horse_Racing/2')
    
    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(5)
    element = driver.find_element_by_xpath('//*[@id="tipsListingContainer-Match"]/thead/tr/th[2]')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    trs = soup.findAll('tbody', attrs={'id': 'tips-table-tbody-match'})[-1].findAll('tr')
    datas = []
    for tr in trs:
        tr_class = tr.get('class')
        if 'cross-promotion-ads-row' in tr_class:
            continue
        
        data = {}
        try:
            title = tr.findAll('h5', attrs={'class': 'event-name'})[-1]
            data['Event'] = title.text.strip()
            xpath = find_xpath(title.find('a', 'tn-trigger'))
            if data['Event'].lower().startswith('race'):
                continue
        except :
            data['Event'] = None
            xpath = None
            continue
        try:
            data['Datetime'] = tr.find('p', attrs={'class' : 'event-date'}).get('content')
            event_date = data['Datetime'].split('T')[0]
            now = datetime.now()
            diff = (now - datetime.strptime(event_date, '%Y-%m-%d')).days
            if diff!=0:
                continue
        except:
            data['Datetime'] = None
        # try:
        #     data['Selection'] = tr.find('h4', attrs={'class': 'selection-name'}).text.strip()
        # except:
        #     data['Selection'] = None
        try:
            data['Expert Count'] = tr.find('p', attrs={'class': 'experts-count'}).text.strip()
        except:
            #data['Expert Count'] = '0 expert'
            continue
            
        # try:
        #     data['Odds'] = tr.find('div', attrs={'class': 'formatted-odds'}).text.strip()
        # except:
        #     data['Odds'] = None
        # try:
        #     data['Tips'] = tr.find('p', attrs={'class': 'tips'}).text.strip().split()[0]
        # except:
        #     data['Tips'] = None
        try:
            data['Confidence Count'] = tr.find('span', attrs={'class': 'confidence-count'}).text.strip()
        except:
            data['Confidence Count'] = None
        try:
            data['Comments Count'] = tr.find('p', attrs={'class': 'comments-count-holder'}).text.strip()
        except:
            data['Comments Count'] = None
        try:
            data['Value Rating'] = tr.findAll('td')[-2].get('data-sort')
        except:
            data['Value Rating'] = None

        mp_tip, n_mp_tips, mp_tip_odds, total_tips, best_tipsters_tip, type_, tipster_name, odds, best_tip_xprt_count, form, age, weight, trainer, jockey, tips_dict, comment = get_best_tip(driver,xpath)

        data['Most Popular Tip'] = mp_tip
        data['Number of tips for most popular'] = n_mp_tips
        data['Most popular odds'] = mp_tip_odds
        data['Total Tips'] = total_tips
        data['Best Tipsters Tip'] = format_name(best_tipsters_tip)
        data['Type'] = type_
        data['Tipster Name'] = tipster_name
        data['Odds'] = odds
        data['Comments text'] = comment
        data['Best Tip Expert Count'] = best_tip_xprt_count
        data['Form'] = form
        data['Age'] = age
        data['Weight'] = weight
        data['Trainer'] = trainer
        data['Jockey'] = jockey
        data['Win Tips'] = tips_dict['win']
        data['EW Tips'] = tips_dict['ew']
        data['NAPS'] = tips_dict['naps']
        datas.append(data)

    df2 = pd.json_normalize(datas)
    df2['1st Place'] = None
    df2['2nd Place'] = None
    df2['3rd Place'] = None
    df2['4th Place'] = None
    df2['Winning Odds'] = None
    df2['Result'] = None
    driver.quit()

    # if os.path.exists('result.csv'):
    #     df2.to_csv('result.csv', mode='a', index=False, header=False)
    # else:
    #     df2.to_csv('result.csv', mode='a', index=False)

    df2.to_csv(OLBG_FILENAME, mode='w', index=False, encoding='utf-8')

def format_name(name):
    res = ''
    for i in name:
        if i.isalnum() or i == ' ':
            res += i
    res = ' '.join([word.capitalize() for word in res.split()])
    return res

def scrape_racing_post():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)

    driver.get('https://www.racingpost.com/fast-results/')
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    divs = soup.findAll('div', attrs={'class': 'rp-timeView__listItem'})
    datas = []
    for div in divs:
        data = {}
        try:
            data['Time Panel'] =  div.find('div', attrs={'class': 'rp-timeView__timePanel'}).find('span').text.strip()
        except:
            data['Time Panel'] =  div.find('div', attrs={'class': 'rp-timeView__timePanel'}).text.strip()
        
        data['Name'] = div.find('div', attrs={'class': 'rp-timeView__raceName'}).text.strip()
        data['Race Title'] = div.find('h4', attrs={'class': 'rp-timeView__raceTitle'}).text.strip()
        try:
            data['1st Place'] = div.find('li', attrs={'data-outcome-desc': '1st'}).find('span', 'rp-raceResult__horseName').text.strip()
            data['1st Place'] = format_name(data['1st Place'].split('\n')[1].strip())
        except:
            data['1st Place'] = ''
        try:
            data['2nd Place'] = div.find('li', attrs={'data-outcome-desc': '2nd'}).find('span', 'rp-raceResult__horseName').text.strip()
            data['2nd Place'] = format_name(data['2nd Place'].split('\n')[1].strip())
        except:
            data['2nd Place'] = ''
        try:
            data['3rd Place'] = div.find('li', attrs={'data-outcome-desc': '3rd'}).find('span', 'rp-raceResult__horseName').text.strip()
            data['3rd Place'] = format_name(data['3rd Place'].split('\n')[1].strip())
        except:
            data['3rd Place'] = ''
        try:
            data['4th Place'] = div.find('li', attrs={'data-outcome-desc': '4th'}).find('span', 'rp-raceResult__horseName').text.strip()
            data['4th Place'] = format_name(data['4th Place'].split('\n')[1].strip())
        except:
            data['4th Place'] = ''
        try:
            data['Winning Odds']  = div.find('li', attrs={'data-outcome-desc': '1st'}).find('span', 'rp-raceResult__horsePrice').text.strip().replace('/','|')
        except:
            data['Winning Odds'] = None
        datas.append(data)

    df1 = pd.json_normalize(datas)
    # df1.to_csv('test.csv')
    driver.quit()
    df2 = pd.read_csv(OLBG_FILENAME)

    dfs = []
    for index, row in df1.iterrows():
        city = row['Name'].split(' ')[0]
        panel = row['Time Panel']
        try:
            sub = df2[df2['Event'].str.contains(city, na=False)]
        except Exception as e:
            print(e)
            continue
        if sub.shape[0] != 0:
            try:
                # sub_sub = sub.copy(deep=False)
                sub_sub = sub[sub['Event'].str.contains(panel, na=False)]
            except Exception as e:
                print(e)
                continue
            if sub_sub.shape[0] != 0:
                event_date = str(sub_sub.iloc[0]['Datetime']).split('T')[0]
                now = datetime.utcnow()
                diff = (now - datetime.strptime(event_date, '%Y-%m-%d')).days
                if diff == 0:
                    print(city, panel)
                    df2['1st Place'] = row['1st Place']
                    df2['2nd Place'] = row['2nd Place']
                    df2['3rd Place'] = row['3rd Place']
                    df2['4th Place'] = row['4th Place']
                    df2['Winning Odds'] = row['Winning Odds']
                    sub = df2[df2['Event'].str.contains(city, na=False)]
                    sub_sub = sub[sub['Event'].str.contains(panel, na=False)]
                    dfs.append(sub_sub)
    
    if dfs != []:
        df = pd.concat(dfs)
        for i, row in df.iterrows():
            try:
                if row['Best Tipsters Tip'] in row['1st Place']:
                    df.loc[i, 'Result'] = 'WIN'
                elif row['Type'] == "EW" and row['Best Tipsters Tip'] in row['1st Place'] or row['Type'] == "EW" and row['Best Tipsters Tip'] in row['2nd Place'] or row['Type'] == "EW" and row['Best Tipsters Tip'] in row['3rd Place']or row['Type'] == "EW" and row['Best Tipsters Tip'] in row['4th Place']:
                    df.loc[i, 'Result'] = 'WIN'
                elif row['1st Place'] == '':
                    df.loc[i, 'Result'] = ''
                else:
                    df.loc[i, 'Result'] = 'LOST'
            except:
                data['Result'] = None
        df.to_csv(OLBG_FILENAME, mode='w', index=False, encoding='utf-8')

if os.path.exists(OLBG_FILENAME):
    print(OLBG_FILENAME, 'exists. Scraping Racing Post...')
    scrape_racing_post()
else:
    print(OLBG_FILENAME, 'does not exist. Scraping OLBG...')
    scrape_olbg()
