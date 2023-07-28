import matplotlib.pyplot as plt
from matplotlib import animation
import re

plt.style.use('fivethirtyeight')

def animate(i):
    # open the file and split by line
    data = open('q1_out.txt','r').read()
    lines = data.split('\n')

    # append x and y values to the list from the file
    xs = []
    ys = []
    for line in lines:
        if not re.search("----------- .* -----------", line) and len(line) > 1:
            x, y = line.split()
            xs.append(x)
            ys.append(int(y))
    
    # make a bar chart and plot
    plt.cla()
    plt.barh(xs, ys, color='royalblue', height=0.4)
    plt.title("Trends")
    plt.xlabel("Number of Tweets")
    plt.plot()

# update the current plot every 2 seconds
ani = animation.FuncAnimation(plt.gcf(), animate, interval=2000)
plt.show()