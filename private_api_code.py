import requests
import datetime
from datetime import date
import json

def lambda_handler(event, context):
    today = date.today()
    d1 = today.strftime("%Y%m%d")
    
    updated_ip_ranges = []
    
    aws_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
    
    gcp_url = 'https://www.gstatic.com/ipranges/cloud.json'

    print("Logging aws urls")
    
    response = requests.get(aws_url)
    y = json.loads(response.text)
    prefixes = y['prefixes']
    for prefix in prefixes:
        updated_ip_ranges.append(prefix['ip_prefix'] +  ',' + prefix['region'] + ',' + prefix['service'] + ',aws,' + d1)
        
    print("AWS logged successfully")
    
    print("Logging GCP URLs")
    
    response = requests.get(gcp_url)
    y = json.loads(response.text)
    prefixes = y['prefixes']
    for prefix in prefixes:
        if 'ipv4Prefix' in prefix:
            updated_ip_ranges.append(prefix['ipv4Prefix'] + ',' + prefix['scope'] + ',' + prefix['service'] + ',gcp,'+ d1)
            
    print("GCP logged successfully")
    
    today = datetime.date.today()
    most_recent_monday = today - datetime.timedelta(days=today.weekday())
    mrm_str = most_recent_monday.strftime("%Y%m%d")
    
    print("Using " + mrm_str + " for Azure date")
    
    azure_url = 'https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_' + mrm_str + '.json'
    
    print("Collecting Azure URLs")
    
    response = requests.get(azure_url)
    try:
        y = json.loads(response.text)
        values = y['values']
        for value in values:
            prefixes = value['properties']['addressPrefixes']
            for prefix in prefixes:
                updated_ip_ranges.append(prefix + ',' + value['properties']['region'] + ',' + value['properties']['systemService']  + ',azure,' + d1)
    except Exception as e:
        #print(response.text)
        print(e)
        print('No new Azure ranges')
        
    print("Azure logged successfully")
        
    azure_gov_url = 'https://download.microsoft.com/download/6/4/D/64DB03BF-895B-4173-A8B1-BA4AD5D4DF22/ServiceTags_AzureGovernment_' + mrm_str + '.json'
    
    response = requests.get(azure_gov_url)
    try:
        y = json.loads(response.text)
        values = y['values']
        for value in values:
            prefixes = value['properties']['addressPrefixes']
            for prefix in prefixes:
                updated_ip_ranges.append(prefix + ',' + value['properties']['region'] + ',' + value['properties']['systemService'] + ',azure_gov,' + d1)
    except Exception as e:
        print(e)
        print('No new Azure Gov ranges')
        
    print("Azure gov logged successfully")
        
    azure_cn_url = 'https://download.microsoft.com/download/9/D/0/9D03B7E2-4B80-4BF3-9B91-DA8C7D3EE9F9/ServiceTags_China_' + mrm_str + '.json'
    
    print('Azure CN URL ' + azure_cn_url)
    
    response = requests.get(azure_cn_url)
    try:
        y = json.loads(response.text)
        values = y['values']
        for value in values:
            prefixes = value['properties']['addressPrefixes']
            for prefix in prefixes:
                updated_ip_ranges.append(prefix + ',' + value['properties']['region'] + ',' + value['properties']['systemService'] + ',azure_cn,' + d1)
    except Exception as e:
        print(e)
        print('No new Azure CN ranges')
        
    print("Azure CN logged successfully")
        
    res = [[0, updated_ip_ranges]]
    #res.append(updated_ip_ranges)
    #print(updated_ip_ranges)
    try:
        return {'statusCode': 200, 'body': json.dumps({'data': res})}
    except Exception as e:
        return {'statusCode': 503, 'body': e}
