# Import required packages
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType
from cassandra_handler import create_cassandra_session, create_cassandra_tables

# Globally define variables that should be handy to change
CASSANDRA_HOST = 'cassandra'
TOPIC_NAME = 'meetup_topic'
CASSANDRA_KEYSPACE = 'meetup_keyspace'
MEETUP_TABLE = 'meetup_table'


# Create a spark session and configure this for cassandra
def create_spark_session():
    spark = SparkSession \
        .builder \
        .appName('Meetup Processing') \
        .config('spark.cassandra.connection.host', CASSANDRA_HOST) \
        .config('spark.cassandra.connection.port', '9042') \
        .getOrCreate()
    return spark


# Process the stream
def process_kafka_stream(spark):
    # Define the schema of the JSON data source for the fields of interest
    schema = StructType([
        StructField('venue', StructType([
            StructField('venue_name', StringType()),
            StructField('lon', StringType()),
            StructField('lat', StringType()),
        ])),
        StructField('response', StringType()),
        StructField('group', StructType([
            StructField('group_city', StringType())
        ]))
    ])

    # Define the Kafka stream
    kafkaStreamDF = spark.readStream.format('kafka') \
        .option('kafka.bootstrap.servers', 'kafka:9092') \
        .option('subscribe', TOPIC_NAME) \
        .option('startingOffsets', 'earliest') \
        .load()

    # Cast the value column to string (it comes in as binary by default)
    kafkaStreamDF = kafkaStreamDF.selectExpr('CAST(value AS STRING)')

    # Extract the JSON data_source based on the schema
    jsonDF = kafkaStreamDF.select(from_json(col('value'), schema).alias('data_source'))

    # Extract individual fields from the 'data_source' column
    responseDF = jsonDF.select('data_source.venue.venue_name', 'data_source.venue.lon', 'data_source.venue.lat',
                               'data_source.response', 'data_source.group.group_city')

    # Filter responses with 'yes' and group by venue_name, lon and lat
    df_grouped = responseDF.where(responseDF.response == 'yes').groupBy('venue_name', 'lon', 'lat',
                                                                        'group_city').count()

    # Order the dataframe by count descending
    df_sorted = df_grouped.orderBy('count', ascending=False)

    # Remove any values that are null for venue_name
    # The decision for this is so that the api can also output the venue_name properly
    df_not_null = df_sorted.filter(df_sorted.venue_name.isNotNull())

    # Save the data_source to Cassandra
    query = df_not_null \
        .writeStream \
        .foreachBatch(lambda df, epoch_id: df.write \
                      .format('org.apache.spark.sql.cassandra') \
                      .options(table=MEETUP_TABLE, keyspace=CASSANDRA_KEYSPACE, host=CASSANDRA_HOST,
                               port=9042) \
                      .mode('append') \
                      .save()) \
        .outputMode('complete') \
        .trigger(processingTime='5 seconds') \
        .start()

    query.awaitTermination()


def main():
    spark = create_spark_session()
    session = create_cassandra_session()
    create_cassandra_tables(session)
    process_kafka_stream(spark)


if __name__ == '__main__':
    main()
