#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 11:04:15 2023

@author: konradburchardtpizzaro-local
"""

#core web vitals
import requests

#mobile Friendly
from bs4 import BeautifulSoup
import pandas as pd
from termcolor import colored

# Import the halo module
from halo import Halo

import json



#https://www.semrush.com/blog/on-page-seo-checklist

# URL of the page you want to check
url = input("Enter the URL of the page you want to check:")


  
#Function that runs all other checklist functions   
def checklist(url):
    '''

    Parameters
    ----------
    url : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    #making sure URL has https
    if not url.startswith("https://"):
        url = "https://" + url
    
    #creating Dataframe where we will store all checks
    df = pd.DataFrame(columns=[])
    
    # Set up the spinner animation
    spinner = Halo(text='', spinner='dots')
    # Start the spinner
    spinner.start()

    #Checklist functions starts here
    df = mobile_friendly(url,df)
    df = bot_accessibility(url,df)
    df = indexation_status(url,df)
    df = robots_meta_tag(url,df)
    df = check_x_robots_tag_noindex(url,df)
    df = check_canonical(url,df)
    df = check_schema_org(url, df)
    df = core_web_vitals(url, df)
    
    
    
    # Stop the spinner
    spinner.stop_and_persist(symbol='🤖'.encode('utf-8'), text='All Checks have been finalized!')
    
    df.to_excel('data.xlsx', index=False)
    
    print(df)
    

    
# =============================================================================
# Mobile Friendly
# =============================================================================

    
def mobile_friendly(url,df):
    '''
    Function that checks if URL is mobile friendly. It uses viewport

    Parameters
    ----------
    url (str): The URL to check.
    df (pandas.DataFrame): The pandas DataFrame to append the result to.

    Returns
    -------
    pandas.DataFrame: The updated pandas DataFrame.

    '''
    print(colored("- Is the Page Mobile Friendly?" ,'black',attrs=['bold']))
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Parse the HTML content of the response
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if the meta viewport tag exists
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_tag is None:
            print(f"{url} is not mobile-friendly ❌")
            a = f"{url} is not mobile-friendly ❌ "
        else:
            a = f"{url} is mobile-friendly ✅"
            print(f"{url} is mobile-friendly ✅ ")
        
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({'URL': [url], 'Mobile Friendly': [a]})
        
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], ignore_index=True) 
        
    except Exception as e:
        # Handle the exception
        print(f"Mobile Friendly Check failed with error: {e}🚫🚫🚫🚫")
        
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({'URL': [url], 'Mobile Friendly': f'Mobile Friendly Check failed with error: {e} '})
          
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], ignore_index=True)  

    return df
    
 
# =============================================================================
# Core Web Vitals
# =============================================================================

def cwv_threshold(value, threshold1, threshold2):
    '''
    Given a value and two thresholds, return a string indicating the quality of the value.
 
    Parameters
    ----------
    value : int or float
        The value to be evaluated.
    threshold1 : int or float
        The lower threshold value.
    threshold2 : int or float
        The upper threshold value.
 
    Returns
    -------
    str
        A string indicating the quality of the value, which can be one of:
        - "good ✅" if the value is less than threshold1.
        - "needs improvement ⚠️" if the value is between threshold1 and threshold2 (inclusive).
        - "poor ❌" if the value is greater than threshold2.
        - "invalid input" if the value is not a number.

   '''
    if value < threshold1:
        return "good ✅"
    elif value >= threshold1 and value <= threshold2:
        return "needs improvement ⚠️"
    elif value > threshold2:
        return "poor ❌"
    else:
        return "invalid input"
    
    
def core_web_vitals(url,df):
    
    '''
    Function that checks the core web vitals of a URL using the PageSpeed Insights API.

    Parameters
    ----------
    url (str): The URL to check.
    df (pandas.DataFrame): The pandas DataFrame to append the result to.

    Returns
    -------
    pandas.DataFrame: The updated pandas DataFrame.

    '''
    
    # Define the endpoint URL for the PageSpeed Insights API
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    
    # Define the parameters for the API request
    params = {
        'url': url,
        'strategy': 'mobile'  # or 'desktop'
    }

    # Make the API request
    response = requests.get(endpoint, params=params)
    
    # Check the response status code
    if response.status_code == 200:
        # Parse the response JSON
        data = response.json()
        # Extract the performance score for DF
        lcp = data['lighthouseResult']['audits']['largest-contentful-paint']['displayValue']
        cls = data['lighthouseResult']['audits']['cumulative-layout-shift']['displayValue']
        si = data['lighthouseResult']['audits']['speed-index']['displayValue']
        fcp = data['lighthouseResult']['audits']['first-contentful-paint']['displayValue']
        tbt = data['lighthouseResult']['audits']['total-blocking-time']['displayValue']
        #tti = data['lighthouseResult']['audits']['interactive']['displayValue']
        #score = data['lighthouseResult']['categories']['performance']['score']
        
        #Extract the scores for thresholds. 
        lcp_int = data['lighthouseResult']['audits']['largest-contentful-paint']['numericValue']
        cls_int = data['lighthouseResult']['audits']['cumulative-layout-shift']['numericValue']
        si_int = data['lighthouseResult']['audits']['speed-index']['numericValue']
        fcp_int = data['lighthouseResult']['audits']['first-contentful-paint']['numericValue']
        tbt_int = data['lighthouseResult']['audits']['total-blocking-time']['numericValue']
        #tti_int= data['lighthouseResult']['audits']['interactive']['numericValue']
        
    
        
        #checking if we are passing Each Value.
        lcp_row = [cwv_threshold(lcp_int,2500,4000), lcp ]
        cls_row = [cwv_threshold(cls_int,0.1,0.25), cls]
        si_row = [cwv_threshold(si_int,3400,5800), si]
        fcp_row = [cwv_threshold(fcp_int,1800,3000), fcp]
        tbt_row = [cwv_threshold(tbt_int,200,600), tbt]
        
    
        # Create a new DataFrame with the row(s) to append
        cwv_new_row = pd.DataFrame({'Largest Contentful Paint': [lcp_row[1]], 'LCP Result': [lcp_row[0]],
                                'Cumulative Layout Shift': [cls_row[1]], 'CLS Results': [cls_row[0]],
                                'Speed Index': [si_row[1]], 'SI Result': [si_row[0]],
                                'First Contentful Paint': [fcp_row[1]], 'FCP Result': [fcp_row[0]],
                                'Total Blocking Time': [tbt_row[1]], 'TBT Result': [tbt_row[0]]})
            
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, cwv_new_row],  axis=1)
        print(colored(f"- Core Web Vitals Performance score for {url}:" ,'black',attrs=['bold']))
        print(f"- Largest Contentful Paint: {lcp} - {lcp_row[0]}")
        print(f'- Cumulative Layout Shift:  {cls} - {cls_row[0]}')
        print(f'- Speed Index:  {si} - {si_row[0]}')
        print(f'- First Contentful Paint:  {fcp} - {fcp_row[0]}')
        print(f'- Total Blocking Time:  {tbt} - {tbt_row[0]}')
    else:
        print(f"Error {response.status_code}: {response.text}")
        
    return df
            
    
    
# =============================================================================
# Check indexation Status of URL
# =============================================================================

def indexation_status(url,df):
    
    '''
    Function that checks if URL is currently indexed on Google.

    Parameters
    ----------
    url (str): The URL to check.
    df (pandas.DataFrame): The pandas DataFrame to append the result to.

    Returns
    -------
    pandas.DataFrame: The updated pandas DataFrame.

    '''
    print(colored(f"- Is the Page indexed in Google?" ,'black',attrs=['bold']))
    try:
        # Define the search query
        query = f"site:{url}"

        # Define the URL for the Google search results page
        google_url = f"https://www.google.com/search?q={query}"

        # Set the user agent header
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

        # Make the HTTP GET request to Google with the user agent header
        response = requests.get(google_url, headers=headers)


        # Parse the HTML using BS4
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the search result divs
        search_results = soup.find('a', href=True, attrs={'data-ved': True, 'jsname': 'ACyKwe'})

        if url in str(search_results):
            url_indexed = True
        else:
            url_indexed = False

        # Print the resultss
        if url_indexed:
            print(f"{url} is indexed in Google. ✅")
            a = f"{url} is indexed in Google. ✅"
        else:
            print(f"{url} is not indexed in Google.❌")
            a = f"{url} is not indexed in Google.❌"
            
            
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({'Indexation': [a]})
        
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1) 
    
    except Exception as e:
        # Handle the exception
        print(f"Indexation Check failed with error: {e}🚫🚫🚫🚫")
        
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({'Indexation': f'Indexation Check failed with error: {e} '})
          
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1)  
        
    return df





def bot_accessibility(url,df):
    # Set the user agents for Googlebot and Bingbot
    user_agents = {
       "GoogleBot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Bingbot":"Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        "Yahoo Slurp":"Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
        "DuckDuckGo":"DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
        "Baidu":"Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
        "Yandex":"Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
        "Applebot":"Mozilla/5.0 (Device; OS_version) AppleWebKit/WebKit_version (KHTML, like Gecko)"
    }
    
    print(colored(f"- Is the page accessible for Bots?:" ,'black',attrs=['bold']))
    

    for key, user_agent in user_agents.items():
        try:
            response = requests.get(url, headers={"User-Agent": user_agent})
            print(key, response)
            
            if response.status_code == 200:
                print(f"{url} is accessible for",  key, " ✅")
                a = f"Response {response.status_code}.  {url} is accessible for  {key} ✅"
            else:
                print(f"The page {url} is not accessible for", key," ❌")
                a = f"Response {response.status_code}.  {url} is not accessible for {key}❌"
                
            # Create a new DataFrame with the row(s) to append
            new_row = pd.DataFrame({key: [a]})
            
            # Concatenate the new DataFrame with the existing DataFrame
            df = pd.concat([df, new_row], axis=1)  
            
                
        except Exception as e:
            # Handle the exception
            print(f"Bot Accessibility Check failed with error: {e}🚫🚫🚫🚫")
            
            # Create a new DataFrame with the row(s) to append
            new_row = pd.DataFrame({ 'Bot Accessibility': f'Bot Accessibility failed with error: {e} '})
              
            # Concatenate the new DataFrame with the existing DataFrame
            df = pd.concat([df, new_row], axis=1)  
            
        
    return df
    
    
def robots_meta_tag(url, df):
    #check 1 Meta robots tag
    
    print(colored("- Indexability #1 -  Does the page contains a no index tag on the header?:" ,'black',attrs=['bold']))
    try:
        response = requests.get(url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_robots = soup.find('meta', attrs={'name': 'robots'})

        if meta_robots and 'noindex' in meta_robots.get('content', ''):
            print(f'The URL {url} is not indexable as it contains the <meta name="robots" content="noindex"> tag in the header. ❌')
            a= f"The URL {url} is not indexable as it contains the <meta name='robots' content='noindex'> tag in the header. ❌"
            
        else:
            print(f'The URL {url} does not contain the <meta name="robots" content="noindex"> tag in the header.✅')
            a = f'The URL {url} does not contain the <meta name="robots" content="noindex"> tag in the header.✅'
            
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({"No index Meta Tag": [a]})
        
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1)  
        
    except requests.exceptions.RequestException as e:
        # Handle the exception
        print(f"No index test failed with errors: {e}🚫🚫🚫🚫")
        
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({ 'No Index Meta Tag': f'No index test failed with errors:: {e} '})
          
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1)  
    return df

    
    
    
def check_x_robots_tag_noindex(url,df):
    
    print(colored("- Indexability #2 -  Does the page contains a HTTP response header: X-Robots-Tag: noindex ?:" ,'black',attrs=['bold']))
    
    try:
        response = requests.get(url)
        
        x_robots_tag = response.headers.get('X-Robots-Tag')

        if x_robots_tag and ('noindex' in x_robots_tag or 'none' in x_robots_tag):
            print(f'The URL {url} is not indexable. It contains the HTTP response header: X-Robots-Tag: noindex ❌')
            a = f"The URL {url} is not indexable. It contains the HTTP response header: X-Robots-Tag: noindex ❌"
        else:
            print(f'The URL {url} is indexable. It does not contain the HTTPS response header  X-Robots-Tag: noindex ✅')
            a = f'The URL {url} is indexable. It does not contain the HTTPS response header  X-Robots-Tag: noindex ✅'
            
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({"No index Response Header": [a]})
        
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1)
            
    except requests.exceptions.RequestException as e:
        # Handle the exception
        print(f"No index Response header test failed with errors: {e}🚫🚫🚫🚫")
        
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({ 'No index response header': f'No index response header failed with errors: {e} '})
          
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1) 
        
    return df

      
def check_canonical(url,df):
    
    print(colored("- Indexability #3 -  Is the page self canonical?" ,'black',attrs=['bold']))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            canonical_tag = soup.find('link', {'rel': 'canonical'})
            canonical_url = canonical_tag.get('href')
            
            if canonical_url == url:    
                print(f'The URL {url} is indexable. The url is self canonicalized. {url} = {canonical_url} ✅')
                a = f'The URL {url} is indexable. The url is self canonicalized. {url} = {canonical_url} ✅'
                
            else:
                print(f'The URL {url} is not indexable. The canonical url ( {canonical_url} ) is different than the page url. {url} ≠ {canonical_url} ❌')
                a = f'The URL {url} is not indexable. The canonical url ( {canonical_url} ) is different than the page url. {url} ≠ {canonical_url} ❌'
                
            #Create a new DataFrame with the row(s) to append
            new_row = pd.DataFrame({"Canonical": [a]})
            
            # Concatenate the new DataFrame with the existing DataFrame
            df = pd.concat([df, new_row], axis=1)  
        
        else:
            print(f'The URL {url} is not indexable.The page has a status code of{response.status_code} ❌')
            a = f'The URL {url} is not indexable.The page has a status code of{response.status_code} ❌'
         
        #Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({"Canonical": [a]})
        
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1)  
            
            
            
    except requests.exceptions.RequestException as e:  
        # Handle the exception
        print(f"No index Response header test failed with errors: {e}🚫🚫🚫🚫")
        
        # Create a new DataFrame with the row(s) to append
        new_row = pd.DataFrame({ 'No index response header': f'No index response header failed with errors: {e} '})
          
        # Concatenate the new DataFrame with the existing DataFrame
        df = pd.concat([df, new_row], axis=1) 
        
    return df  

def check_schema_org(url, df):
    print(colored("- Schema.org Check -", 'black', attrs=['bold']))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            schema_types = set()

            # JSON-LD
            for script_tag in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script_tag.string)
                    if isinstance(data, list):
                        for item in data:
                            if '@type' in item:
                                schema_types.add(item['@type'])
                    elif '@type' in data:
                        schema_types.add(data['@type'])
                except json.JSONDecodeError:
                    pass

            # Microdata
            for microdata_tag in soup.find_all(attrs={"itemtype": True}):
                schema_types.add(microdata_tag['itemtype'])

            # RDFa
            for rdfa_tag in soup.find_all(attrs={"typeof": True}):
                schema_types.add(rdfa_tag['typeof'])

            if schema_types:
                print(f"The URL {url} has schema.org structure(s): {', '.join(schema_types)} ✅")
                a = f"The URL {url} has schema.org structure(s): {', '.join(schema_types)} ✅"
            else:
                print(f"The URL {url} does not have any identifiable schema.org structures ❌")
                a = f"The URL {url} does not have any identifiable schema.org structures ❌"
        else:
            print(f"The URL {url} could not be accessed. The page has a status code of {response.status_code} ❌")
            a = f"The URL {url} could not be accessed. The page has a status code of {response.status_code} ❌"

    except requests.exceptions.RequestException as e:
        print(f"Schema.org check failed with errors: {e} 🚫")
        a = f"Schema.org check failed with errors: {e} 🚫"

    # Create a new DataFrame with the row(s) to append
    new_row = pd.DataFrame({"Schema.org": [a]})

    # Concatenate the new DataFrame with the existing DataFrame
    df = pd.concat([df, new_row], axis=1)

    return df
    
    
   
    
     
            
checklist(url)
    
        
    
