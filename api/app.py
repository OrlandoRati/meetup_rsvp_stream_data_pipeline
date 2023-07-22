# Import required packages
from flask import Flask, jsonify, render_template
from cassandra.cluster import Cluster
import pandas as pd

# Globally define variables that should be handy to change
CASSANDRA_HOST = 'cassandra'
CASSANDRA_KEYSPACE = 'meetup_keyspace'
MEETUP_TABLE = 'meetup_table'

app = Flask(__name__)


# Define route to retrieve data that could possibly be used by another
# application to display the most popular venues on a map
# 'lat' and 'lon' seem appropriate to make use of if the requirement is to display on a map
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # Create cassandra connection
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect(CASSANDRA_KEYSPACE)

        # Fetch data_source from your table
        rows = session.execute(f'SELECT * FROM {MEETUP_TABLE}')

        # Convert rows to a list of dicts
        data = [{'venue_name': row.venue_name, 'lon': row.lon, 'lat': row.lat, 'count': row.count,
                 'group_city': row.group_city} for row in rows]

        # If there is no data display error message
        if not data:
            return jsonify({
                'error': 'The response is empty so data has not yet been saved to the database. Please try again later.'}), 503
        else:
            # Return response as json
            return jsonify(data)

    # Catch exception
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 503

# Define route to display a simple table with the most popular venues
@app.route('/api/top_venues', methods=['GET'])
def get_top_venues():
    try:
        # Create cassandra connection
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect(CASSANDRA_KEYSPACE)

        # Fetch data from Cassandra into a Pandas DataFrame
        rows = session.execute(f'SELECT * FROM {MEETUP_TABLE}')
        df = pd.DataFrame(list(rows))

        # If there is no data display error message
        if df.empty:
            return jsonify({
                'error': 'The response is empty so data has not yet been saved to the database. Please try again later.'}), 503
        else:
            # Sort the DataFrame by 'count' in descending order
            df_sorted = df.sort_values(by='count', ascending=False)

            # Convert the sorted DataFrame to a list of dictionaries
            data = df_sorted.to_dict(orient='records')

            # Render the template with the data and display the table
            return render_template('top_venues.html', data=data)

    # Catch exception
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
