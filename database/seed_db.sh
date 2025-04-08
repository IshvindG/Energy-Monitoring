source .env

echo "Seeding database with seeding.sql..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f seeding.sql


echo "Seeding fuel types using fuel_types.py..."
python3 fuel_types.py

echo "Database has been seeded successfully."