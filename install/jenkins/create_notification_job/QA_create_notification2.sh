#!/bin/sh
echo "Exporting Envirment Variable..."
export RA_APIS_ENVIRON=QA
echo $RA_APIS_ENVIRON

echo
echo
echo "***** CREATE NOTIFICATIONS2 script *****"
date

echo "***** Copying configuration *****"
cp /opt/config_ra.py .
cp /opt/config_ra.py ra/ra/settings

echo "***** Creating python virtual environment *****"
/usr/local/bin/python3.7 -m venv ra_virtual_env

echo "***** Virtual environment created, install requirements *****"
ra_virtual_env/bin/pip install -r requirements.txt

echo "***** Jenkins will run automatically create_notifications2 *****"
cd ra
../ra_virtual_env/bin/python manage.py create_notifications2
