"""
    This Spark app connects to a script running on another (Docker) machine
    on port 9009 that provides a stream of raw tweets text. That stream is
    meant to be read and processed here, where top trending hashtags are
    identified. Both apps are designed to be run in Docker containers.

    To execute this in a Docker container, do:
    
        docker run -it -v $PWD:/app --link twitter:twitter eecsyorku/eecs4415

    and inside the docker:

        spark-submit spark_app.py

    For more instructions on how to run, refer to final tutorial 8 slides.

    Made for: EECS 4415 - Big Data Systems (York University EECS dept.)
    Based on: https://www.toptal.com/apache/apache-spark-streaming-twitter
    Original author: Hanee' Medhat

"""

from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row,SQLContext
from textblob import TextBlob
import sys
import requests


# create spark configuration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# create the Streaming Context from spark context, interval size 2 seconds
ssc = StreamingContext(sc, 2)
# setting a checkpoint for RDD recovery (necessary for updateStateByKey)
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("twitter",9009)

# create a dictionary of topics based on the hashtags file
topics = []
with open('hashtags.txt') as file:
    next(file)
    for line in file: 
        tags = line.split()
        for tag in tags:
            topics.append(tag.strip())

# filter the tweets based on hashtags
def filter_tweets(tweet):
    for word in tweet.split():
        if word in topics:
            return True

def assign_topic(tweet):
    pos = 0
    for word in tweet.split():
        for i in range(0, len(topics)):
            if word == topics[i]:
                pos = i
    
    if pos >= 0 and pos < 10:
        return 'Politics'
    if pos >= 10 and pos < 20:
        return 'Sports'
    if pos >= 20 and pos < 30:
        return 'Technology'
    if pos >= 30 and pos < 40:
        return 'COVID-19'
    if pos >= 40 and pos < 50:
        return 'Videogames'

hashtags = dataStream.filter(filter_tweets)

# analyze the sentiment of each tweet using TextBlob
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity < 0:
        return 'negative'
    else:
        return 'neutral'

# map each hashtag to be a pair of (hashtag,1)
hashtag_counts = hashtags.map(lambda x: (assign_topic(x) + " " + analyze_sentiment(x), 1))

# adding the count of each hashtag to its last count
def aggregate_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)

# do the aggregation, note that now this is a sequence of RDDs
hashtag_totals = hashtag_counts.updateStateByKey(aggregate_tags_count)

#creates new files for graph data and output data
output = open('q2_out.txt', 'a+')
output.truncate(0)

# process a single time interval
def process_interval(time, rdd):
    # print a separator to STDOUT and to q1_out.txt
    print("----------- %s -----------" % str(time))
    output.write("----------- %s -----------\n" % str(time))
    try:
        # sort counts (desc) in this time instance and take top 10
        # sorted_rdd = rdd.sortBy(lambda x:x[1], False)

        # print it nicely to STDOUT and to q1_out.txt
        for tag in rdd.take(1000):
            print('{:<40} {}'.format(tag[0], tag[1]))
            output.write('{:<40} {}\n'.format(tag[0], tag[1]))
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)

# do this for every single interval
hashtag_totals.foreachRDD(process_interval)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
