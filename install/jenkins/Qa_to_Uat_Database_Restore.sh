# This is a database backup script that takes a dump from a QA server
# And stored directly on UAT server
echo
echo "********* RA DATABASE RESTORE **********"
echo
echo "This is a database backup script that takes a dump from a QA server 
        And stored directly on UAT server"
echo
echo
script_date=$(date)
echo "Date of running script :: $script_date"
echo
echo
echo
echo ">>> Start QA Server Backup  >>>"
echo
echo
echo

# QA Server configuration credientials

USER="$(python -c 'from config_ra import main_conf;print(main_conf["POSTGRES_USER"])')"
PASS="$(python -c 'from config_ra import main_conf;print(main_conf["POSTGRES_PASSWORD"])')"
QA_DB="$(python -c 'from config_ra import main_conf;print(main_conf["POSTGRES_QA_DATABASE"])')"
HOST="$(python -c 'from config_ra import main_conf;print(main_conf["POSTGRES_DB_HOST"])')"

# UAT Server configuration credientials

UAT_DB="$(python -c 'from config_ra import main_conf;print(main_conf["POSTGRES_UAT_DATABASE"])')"

##########################################
#        QA server dump command        #
##########################################
# -Ft is for tar format
# PGPASSWORD=${PROD_PG_PASS} pg_dump -Ft -U ${PROD_PG_USER} -w -h ${PROD_PG_HOST} -p 5432 ${PROD_PG_DB} > ./prod-local.dump 
PGPASSWORD=${PASS} pg_dump -U ${USER} -w -h ${HOST} -p 5432 -d ${QA_DB} > ./$(date "+%d-%b-%Y").psql # this is correct

echo
echo
echo ">>>  Backup Completed ..! >>>"
echo
echo
echo ">>> Start Restoring on UAT >>>"
echo
echo
echo "Drop Schema"

PGPASSWORD=${PASS} psql -U ${USER} -h ${HOST} -p 5432 -d ${UAT_DB} -c "DROP SCHEMA public CASCADE;CREATE SCHEMA public;"

echo "Schema Drop complete"


##########################################
#        UAT server restore command       #
##########################################


PGPASSWORD=${PASS} psql -U ${USER} -h ${HOST} -p 5432 -d ${UAT_DB} < ./$(date "+%d-%b-%Y").psql # this is correct

echo
echo
echo ">>>> Restore Database complete >>>"













