# db-enum: Database Enumeration Tool

db-enum is a security-focused database enumeration tool designed for penetration testing and bug bounty programs. It allows you to gather basic information about various database types without accessing sensitive data, demonstrating potential impact to clients or bounty programs while preserving privacy.

## Supported Databases

- MySQL
- PostgreSQL
- Microsoft SQL Server
- MongoDB
- Redis
- Elasticsearch
- Cassandra
- Neo4j
- CouchDB
- InfluxDB

## Features

- Automatic database type detection
- Individual commands for each supported database type
- Collects schema information, table names, and approximate sizes without accessing row data
- Docker Compose setup for easy testing with all supported databases

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/db-enum.git
   cd db-enum
   ```

2. Install PDM if you haven't already:

   ```
   pip install pdm
   ```

3. Install the project dependencies:
   ```
   pdm install
   ```

## Usage

To use db-enum, you can either use the `magic` command to automatically detect the database type, or specify the database type explicitly.

### Automatic Detection

```
pdm run db-enum magic --host localhost --port <port> --user <username> --password <password> --database <dbname>
```

### Specific Database Type

```
pdm run db-enum <dbtype> --host localhost --port <port> --user <username> --password <password> --database <dbname>
```

Replace `<dbtype>` with one of: mysql, postgres, mssql, mongodb, redis, elasticsearch, cassandra, neo4j, couchdb, influxdb

## Testing

```
make test
```

This runs `docker compose up` and tests the script against all db types.

## Adding New Database Types

To add support for a new database type:

1. Create a new Python file in `src/db_enum/db/` named after the database (e.g., `newdb.py`).
2. Implement the `check_connection` and `enumerate` functions in this file.
3. The new database type will be automatically detected and added to the CLI.
4. Add to docker-compose.yml and test.

# Disclaimer

This tool is intended for ethical hacking and security analysis purposes on authorized systems only. Unauthorized use of this tool to access or modify systems without permission is illegal and unethical. Always obtain proper authorization before using this tool on any system.

For any issues or contributions, please refer to the project's repository.
