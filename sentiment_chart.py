import matplotlib.pyplot as plt
from matplotlib import animation
import re

plt.style.use('fivethirtyeight')

def animate(i):
    data = open('q2_out.txt', 'r').read()
    lines = data.split('\n')

    # list and dictionary to store data
    labels = []
    neutral = {}
    positive = {}
    negative = {}

    for line in lines:
        if not re.search("----------- .* -----------", line) and len(line) > 1:
            label, sentiment, amount = line.split()
            # if it is a new label then store it to the list and 
            # initialize all of its dictionary values to 0
            if label not in labels:
                labels.append(label)
                positive[label] = 0
                neutral[label] = 0
                negative[label] = 0
            
            # add values to the dictionary
            if sentiment == 'positive':
                positive[label] = int(amount) 
            if sentiment == 'neutral':
                neutral[label] = int(amount) 
            if sentiment == 'negative':
                negative[label] = int(amount) 

    negative_bottom = []
    for i in range(0, len(labels)):
        negative_bottom.append(list(positive.values())[i] + list(neutral.values())[i])

    plt.cla()
    plt.bar(labels, list(positive.values()), label='Positive', width=0.4, color='forestgreen')
    plt.bar(labels, list(neutral.values()), bottom=list(positive.values()), label='Neutral', width=0.4, color='royalblue')
    plt.bar(labels, list(negative.values()), bottom=negative_bottom, label='Negative', width=0.4, color='coral')
    plt.title("Sentiment of Topics")
    plt.ylabel("Number of Tweets")
    plt.legend()
    plt.plot()

# update the current plot every 2 seconds
ani = animation.FuncAnimation(plt.gcf(), animate, interval=2000)
plt.show()