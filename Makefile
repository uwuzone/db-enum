.PHONY: test

test:
	# @echo "Waiting for databases to be ready..."
	# @sleep 30
	@pdm db-enum mysql --host localhost --port 3306 --user root --password rootpassword --database testdb && echo 'mysql ok' || echo 'mysql failed'
	@pdm db-enum postgres --host localhost --port 5432 --user postgres --password rootpassword --database testdb && echo 'postgres ok' || echo 'postgres failed'
	@pdm db-enum mssql --host localhost --port 1433 --user sa --password "YourStrong!Passw0rd" --database master && echo 'mssql ok' || echo 'mssql failed'
	@pdm db-enum mongodb --host localhost --port 27017 --user root --password rootpassword --database admin && echo 'mongodb ok' || echo 'mongodb failed'
	@pdm db-enum redis --host localhost --port 6379 --user default --password "" --database 0 && echo 'redis ok' || echo 'redis failed'
	@pdm db-enum elasticsearch --host localhost --port 9200 --user elastic --password changeme --database default && echo 'elasticsearch ok' || echo 'elasticsearch failed'
	@pdm db-enum cassandra --host localhost --port 9042 --user cassandra --password cassandra --database system  && echo 'cassandra ok' || echo 'cassandra failed'
	@pdm db-enum neo4j --host localhost --port 7687 --user neo4j --password testpassword --database neo4j && echo 'neo4j ok' || echo 'neo4j failed'
	@pdm db-enum couchdb --host localhost --port 5984 --user admin --password password --database _users && echo 'couchdb ok' || echo 'couchdb failed'
	@pdm db-enum influxdb --host localhost --port 8086 --user admin --password password --database testdb && echo 'influxdb ok' || echo 'influxdb failed' && echo 'influxdb ok' || echo 'influxdb failed'