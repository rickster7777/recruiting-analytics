from os import environ

if "RA_APIS_ENVIRON" in environ.keys():
    if environ["RA_APIS_ENVIRON"] == "local":
        from .local import *

    if environ["RA_APIS_ENVIRON"] == "DEV":
        from .dev import *

    if environ["RA_APIS_ENVIRON"] == "QA":
        from .qa import *

    if environ["RA_APIS_ENVIRON"] == "UAT":
        from .uat import *

    if environ["RA_APIS_ENVIRON"] == "PROD":
        from .prod import *

else:
    raise NotImplementedError(
        'No RA_APIS_ENVIRON variable found, exiting the program'
    )
