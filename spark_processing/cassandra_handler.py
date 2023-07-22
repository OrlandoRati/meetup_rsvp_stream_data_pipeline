# Import required packages
import time
from cassandra.cluster import Cluster

# Globally define variables that should be handy to change
CASSANDRA_HOST = 'cassandra'
CASSANDRA_KEYSPACE = 'meetup_keyspace'
MEETUP_TABLE = 'meetup_table'


# Create a cassandra session
# Implement a retry mechanism to take into account startup time for the service
def create_cassandra_session(max_retries=20, retry_timeout=5):
    for attempt in range(max_retries):
        try:
            print(f'Attempt {attempt + 1} to create Cassandra session...')
            cluster = Cluster([CASSANDRA_HOST])
            session = cluster.connect()
            return session

        # Catch exception if connection fails
        except Exception as e:
            print(f'Attempt {attempt + 1}/{max_retries} failed. Retrying in {retry_timeout} seconds. Error: {str(e)}')
            time.sleep(retry_timeout)
    raise Exception(f'Failed to connect to Cassandra after {max_retries}')


# Prepare the cassandra keyspace and table required
def create_cassandra_tables(session):
    # Create keyspace
    session.execute(f'''
                CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
            ''')

    # Create table
    session.execute(f'''
            CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{MEETUP_TABLE} (
                venue_name text,
                lon text,
                lat text,
                group_city text,
                count int,
                PRIMARY KEY (venue_name, lon, lat, group_city)
            );
        ''')
