.PHONY: test test-mysql test-postgres test-mssql test-mongodb test-redis test-elasticsearch test-neo4j test-couchdb test-influxdb test-cassandra

define db_test
pdm db-enum --verbose $(1) --host localhost --port $(2) --user $(3) --password $(4) --database $(5) >/dev/null && echo '$(1) ok' || echo '$(1) failed'
endef

test-mysql:
	$(call db_test,mysql,3306,root,rootpassword,testdb)

test-postgres:
	$(call db_test,postgres,5432,postgres,rootpassword,testdb)

test-mssql:
	$(call db_test,mssql,1433,sa,"YourStrong!Passw0rd",master)

test-mongodb:
	$(call db_test,mongodb,27017,root,rootpassword,admin)

test-redis:
	$(call db_test,redis,6379,default,"",0)

test-elasticsearch:
	$(call db_test,elasticsearch,9200,elastic,changeme,default)

test-neo4j:
	$(call db_test,neo4j,7687,neo4j,testpassword,neo4j)

test-couchdb:
	$(call db_test,couchdb,5984,admin,password,_users)

test-influxdb:
	$(call db_test,influxdb,8086,admin,password,testdb)

test-cassandra:
	$(call db_test,cassandra,9042,cassandra,cassandra,system)

test: test-mysql test-postgres test-mssql test-mongodb test-redis test-elasticsearch test-neo4j test-couchdb test-influxdb test-cassandra
