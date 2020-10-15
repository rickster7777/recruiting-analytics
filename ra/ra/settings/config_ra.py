""" RA secret file
This script holds all the application secrets.
DO NOT COMMIT THIS FILE
Usage:
from config_ra import main_conf as config
SECRET_KEY = config.get('SECRET_KEY')
"""

main_conf = dict()

main_conf['SECRET_KEY'] = 'x!8z78tlkplfjdm^qcmx#b02%i)l^583pa1mo*k2rt7+jze*^w'


main_conf['POSTGRES_USER'] = 'postgres'

main_conf['POSTGRES_PASSWORD'] = 'adminasdfZXCV'

main_conf['POSTGRES_DEV_DATABASE'] = 'RA_DB_DEV'

main_conf['POSTGRES_QA_DATABASE'] = 'RA_DB_QA'

main_conf['POSTGRES_UAT_DATABASE'] = 'RA_DB_UAT'

main_conf['POSTGRES_STAGING_DATABASE'] = 'RA_DB_STAGING'

main_conf['POSTGRES_DB_HOST'] = 'ra-db.cw4nxhdibxun.us-east-2.rds.amazonaws.com'


# SendGrid API Key
main_conf['SENDGRID_APIKEY'] = 'SG.x51GV6wFSLqOlrKjGx9TZw.1cannaEYrxKlG1faW8eL0F1vjKJ6Hf000hOfm19W5iE'

# QA SendGrid API Key
main_conf['QA_SENDGRID_APIKEY'] = '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'
# Strip Keys
main_conf['STRIPE_SECRET_KEY'] = 'sk_test_c6ijnoJJ7dMARXWT8weDHPUf00h6tVPsJi'
main_conf['STRIPE_PUBLISHABLE_KEY'] = 'pk_test_jQ6dFpuhSTwAUwnPFckxn0ge00UPZSoXX3'


# Twitter Consumer APi Keys
main_conf['twitter_consumer_key'] = '6MAyJL1a5deceI1xtUGcXrr2b'
main_conf['twitter_consumer_secret'] = 'Kqh8I7CnpMOkZUrdOB3WYNxXGEolx9LVkhpXtyrvPyUqLve8G1'
main_conf['twitter_access_token'] = '65577920-2hM9ZAWgKg6slidCzjvDNipf9reKsSEKy00ZwQbuA'
main_conf['twitter_access_secret'] = 'XjRBnM9VBr6kmH42ljQwuPJ76IWDBftYORe0VIbvLQXGX'

# Personality Insights Server Key
main_conf['pi_server_key'] = 'VKZuTXxlXmq-3waMOPqZsz91_obOdV5ywq6ZLusqiGZ8'


main_conf['ADMIN_USERS'] = [
    {
        'username': 'admin',
        'password': 'tryornot',
        'email': 'admin@ra.com',
        'first_name': 'admin',
        'last_name': 'only',
    },
    {
        'username': 'tester',
        'password': 'donttry',
        'email': 'qa@ra.com',
        'first_name': 'qa',
        'last_name': 'only',

    },
    {
        'username': 'developer',
        'password': 'alwaystry',
        'email': 'dev@ra.com',
        'first_name': 'dev',
        'last_name': 'ops',

    },
]

main_conf['STRIPE_API_KEY'] = 'sk_test_I9LnMCYLbQFsDCcrSjOerTHA00UX2uU3XM'
# main_conf['STRIPE_MONTHLY_SUBSCRIPTION_ID'] = 'monthly'
# main_conf['STRIPE_YEARLY_SUBSCRIPTION_ID'] = 'yearly'
main_conf['STRIPE_MONTHLY_SUBSCRIPTION_ID'] = 'plan_G8kfGnjD0JBaR8'
main_conf['STRIPE_YEARLY_SUBSCRIPTION_ID'] = 'plan_G8kgdo8soFezv5'


# S3 media upload credientials
main_conf['AWS_ACCESS_KEY_ID'] = 'AKIAWLYJ4L7KZEB6ROHV'
main_conf['AWS_SECRET_ACCESS_KEY'] = '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'
main_conf['AWS_S3_REGION_NAME'] = 'us-east-2'


main_conf['ATHLETICISM_API'] = \
    "http://ec2-3-135-241-146.us-east-2.compute.amazonaws.com:8000/athleticism_api/"

main_conf['API_USER'] = 'admin'
main_conf['API_PASSWORD'] = 'nimdaadmin'
