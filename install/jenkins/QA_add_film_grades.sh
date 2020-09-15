echo "Exporting Envirment Variable..."
export RA_APIS_ENVIRON=QA
echo $RA_APIS_ENVIRON

echo
echo
echo "***** ADD FILM GRADES script *****"
date

echo "***** Copying configuration *****"
sudo cp /opt/config_ra.py .
sudo cp /opt/config_ra.py ra/ra/settings

echo "***** Creating python virtual environment *****"
/usr/local/bin/python3.7 -m venv ra_virtual_env

echo "***** Virtual environment created, install requirements *****"
ra_virtual_env/bin/pip install -r requirements.txt

echo "***** Jenkins will run automatically add_film_grades command *****"
cd ra
../ra_virtual_env/bin/python manage.py new_player_import_2_may ./players/management/commands/updated_player_unique28April.xlsx
