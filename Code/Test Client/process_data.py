import matplotlib.pyplot as plt
import re

files = ["data/" + str(24002+2*i) + ".log" for i in range(100)]
files = list(map(lambda f: open(f,"r"),files))
data = list(map(lambda f: f.readlines()[1:],files))
data = list(map(lambda f: list(map(lambda x: re.sub(" +"," ", x).replace("\n","").split(" ")[1:],f)), data))
data = list(map(lambda f: list(map(lambda x: list(map(lambda y: float(y),x)), f)), data))
minlen = min(list(map(lambda f: len(f), data)))
minCPU = [2**100] * minlen
maxCPU = [0] * minlen
avgCPU = [0] * minlen

for i in range(0,minlen):
    for run in data:
        minCPU[i] = min(run[i][1],minCPU[i])
        maxCPU[i] = max(run[i][1],maxCPU[i])
        avgCPU[i] += run[i][1]
    avgCPU[i] /= minlen
smoothedMax = []
smoothedAvg = []
amt = 0
for i in range(0,minlen,60):
    smoothedMax.append(sum(maxCPU[i:i+60])/60.)
    smoothedAvg.append(sum(avgCPU[i:i+60])/60.)
    amt += 1

plt.plot(list(range(amt)), smoothedMax, label="Max. CPU Usage (%)")
plt.plot(list(range(amt)), smoothedAvg, label="Avg. CPU Usage (%)")
plt.xlabel("Time (min)")
plt.ylabel("Maximum CPU Utilisation (%)")
plt.title("100 Node Network Performance")
plt.legend()
plt.show()
    
