import json
import snowflake.connector
import socket
import boto3
import base64
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "XXXXXXXX"
    region_name = "XXXXXXXX"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
    # Your code goes here. 
    
    


def lambda_handler(event, context):
    
    print("Retrieving secrets")
    
    secrets = get_secret()
    user = secrets['snowflake_user']
    password = secrets['snowflake_pw']
    account = secrets['snowflake_account']
    warehouse = secrets['snowflake_wh']
    
    print("Connecting to Snowflake")
    
    ctx = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database="CSP_PUBLIC_IPS",
            schema="PUBLIC"
            )

    cur = ctx.cursor()
    
    api_input = json.loads(event['body'])
    
    str_builder = '['
    
    for ip_addr in api_input['ip_addresses']:
        try:
            socket.inet_aton(ip_addr)
            # legal
        except socket.error:
            return {
                'statusCode': 403,
                'body': json.dumps("Please ensure all IP addresses are valid")
            }
        str_builder += '"'
        str_builder += ip_addr
        str_builder += '"'
        str_builder += ','
    str_builder += ']'
    
    sql_input = f"""set var1 = '{str_builder}';"""
    
    print("Setting list of IPs")
    print(sql_input)
    
    try:
        cur.execute(sql_input)
    except Exception as e:
        print("Failed to set var")
        print(e)
        return {
            'statusCode': 503,
            'body': "Failed to execute"
        }
    
    if 'cached' in api_input.keys() and (api_input['cached'] == 'n' or api_input['cached'] == False):
        print('Using live data')
        select_table = 'csp_public_ips.public.collect_csp_cidr_ranges()'
     
    else:
        print('Using cached table')
        select_table = '* from csp_public_ips.public.public_csp_ranges'
        
    sql_retrieve = f"""with helper as (
    select
        {select_table} as csp_ranges
),
helper_two as (
    select
        split(value, ',') as array_val
    from
        helper,
        lateral flatten(csp_ranges)
),
helper_three as (
    select
        array_val[3]::varchar as csp,
        case
            when array_val[1] != '' then array_val[1]::varchar
            else NULL
        end as region,
        case
            when array_val[2] != '' then array_val[2]::varchar
            else NULL
        end as service,
        array_val[0]::varchar as ip_range,
        array_val[4]::varchar as date
    from
        helper_two
),
helper_input as (
    select
        parse_json($var1) as input
),
helper_input_two as (
    select
        *
    from
        helper_input,
        lateral flatten(input)
),
helper_four as (
    select
        OBJECT_CONSTRUCT(
            'ip_address',
            value::varchar, 'data',
            CASE WHEN ARRAY_SIZE(ARRAY_AGG(csp)) = 0 then OBJECT_CONSTRUCT('data', NULL) else
            OBJECT_CONSTRUCT(
                'cloud',
                max(csp),
                'service',
                array_agg(distinct service),
                'region',
                array_agg(distinct region),
                'ip_range',
                array_agg(distinct ip_range),
                'date',
                max(date)
            ) end
        )
    from
        helper_input_two
        left outer join helper_three on parse_ip(VALUE, 'inet') ['ipv4'] between parse_ip(ip_range, 'cidr') ['ipv4_range_start']
        and parse_ip(ip_range, 'cidr') ['ipv4_range_end']
    group by
        value
)
select
    *
from
    helper_four"""
 
    print("Executing ")
    
    try:
        cur.execute(sql_retrieve)
    except Exception as e:
        print("Failed to execute query")
        print(e)
        return {
            'statusCode': 503,
            'body': "Failed to execute"
        }
    
    res_obj = []
    
    try:
        df = cur.fetchall()
        
        for row in df:
            json_row = json.loads(row[0])
            res_obj.append(json_row)
        print(res_obj)
        
    except Exception as e:
        print("Failed to parse query result")
        print(e)
        return {
            'statusCode': 503,
            'body': "Failed to execute"
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(res_obj)
    }
