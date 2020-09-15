from storages.backends.s3boto3 import S3Boto3Storage
from os import environ


class RAMediaStorage(S3Boto3Storage):
    
    if "RA_APIS_ENVIRON" in environ.keys():

        if environ["RA_APIS_ENVIRON"] == "DEV":
            location = 'media/dev-media'
       
        if environ["RA_APIS_ENVIRON"] == "QA":
            location = 'media/qa-media'

        if environ["RA_APIS_ENVIRON"] == "UAT":
            location = 'media/uat-media'

        if environ["RA_APIS_ENVIRON"] == "PROD":
            location = 'media/prod-media'
            
    file_overwrite = False
