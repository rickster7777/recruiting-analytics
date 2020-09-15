echo "Exporting Envirment Variable..."
export RA_APIS_ENVIRON=UAT
echo $RA_APIS_ENVIRON

echo
echo
echo "***** RA Create Notification script *****"
date

echo "***** Copying configuration *****"
sudo cp /opt/config_ra.py .
sudo cp /opt/config_ra.py ra/ra/settings

echo "***** Creating python virtual environment *****"
/usr/local/bin/python3.7 -m venv ra_virtual_env

echo "***** Virtual environment created, install requirements *****"
ra_virtual_env/bin/pip install -r requirements.txt

echo "***** Copying Chrome Driver to ra_virtual_env/bin/ Directory *****"
cp /opt/chromedriver ./ra_virtual_env/bin/

echo "***** Start create_notification job  *****"
cd ra
../ra_virtual_env/bin/python manage.py create_notifications
