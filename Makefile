.PHONY: up down test

up:
	docker-compose up -d

down:
	docker-compose down

test: up
	@echo "Waiting for databases to be ready..."
	@sleep 30
	pdm run db-enum mysql --host localhost --port 3306 --user root --password rootpassword --database testdb
	pdm run db-enum postgres --host localhost --port 5432 --user postgres --password rootpassword --database testdb
	pdm run db-enum mssql --host localhost --port 1433 --user sa --password "YourStrong!Passw0rd" --database master
	pdm run db-enum mongodb --host localhost --port 27017 --user root --password rootpassword --database admin
	pdm run db-enum redis --host localhost --port 6379 --user default --password "" --database 0
	pdm run db-enum elasticsearch --host localhost --port 9200 --user elastic --password changeme --database default
	pdm run db-enum cassandra --host localhost --port 9042 --user cassandra --password cassandra --database system
	pdm run db-enum neo4j --host localhost --port 7687 --user neo4j --password testpassword --database neo4j
	pdm run db-enum couchdb --host localhost --port 5984 --user admin --password password --database _users
	pdm run db-enum influxdb --host localhost --port 8086 --user admin --password password --database testdb