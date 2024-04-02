echo "Dropping"
dropdb pricelist_staging
echo "Creating"
createdb pricelist_staging
echo "Populating"
psql -d pricelist_staging < pricelist_staging.psql
