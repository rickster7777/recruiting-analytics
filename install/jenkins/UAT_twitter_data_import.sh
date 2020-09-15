echo "Exporting Envirment Variable..."
export RA_APIS_ENVIRON=UAT
echo $RA_APIS_ENVIRON

echo
echo
echo "***** RA TWITTER DATA  IMPORT script *****"
date

echo "***** Copying configuration *****"
sudo cp /opt/config_ra.py .
sudo cp /opt/config_ra.py ra/ra/settings

echo "***** Creating python virtual environment *****"
/usr/local/bin/python3.7 -m venv ra_virtual_env

echo "***** Virtual environment created, install requirements *****"
ra_virtual_env/bin/pip install -r requirements.txt

echo "***** Jenkins will run automatically import_twitter_data command  *****"
cd ra
../ra_virtual_env/bin/python manage.py import_twitter_data

