import subprocess
import json
import matplotlib.pyplot as plt

Seed = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180,
        190, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000,
        6000, 7000, 8000, 9000, 10000] # All seed required to do audits
State = 'NSW' # The state
Data = '/Users/tianjiazhang/Desktop/DATA' # The path of data file

Timeout = 1800 # Timeout threshold
Timeoutseed = [] # List of all timeout seed
Timeoutsize = 10000000 # Default timeout sample size

Allsamplesize = [] # List of all sample size

for i in Seed: # Run different audits automatically
    try:
        name = "aus-senate-audit quick --seed " + str(i) + " --state " + State + " --data " + Data
        runaudit = subprocess.call([name], shell = True, timeout= Timeout)
        print (runaudit)
        filename = "audit_"+State+"_seed_" + str(i)
        f = open (filename + "/info.json", "r")
        setting = json.load(f)
        sample = setting['sample_size']
        Allsamplesize.append(sample)

    except subprocess.TimeoutExpired:
        Timeoutseed.append(i)
        print('Timeout seed' + str(Timeoutseed))
        filename = "audit_"+State+"_seed_" + str(i)
        f = open(filename + "/info.json", "r")
        setting = json.load(f)
        sample = setting['sample_size']
        Allsamplesize.append(sample)
        if sample < Timeoutsize:
            Timeoutsize = sample

print('Timeout seed' + str(Timeoutseed)) #Print all timeout seeds
print('All sample size' + str(Allsamplesize)) #Print all sample size



plt.xlabel('Sample Size') #Graph
plt.ylabel('Frequency')
plt.title('State '+ State +' - Sample Size Graph')

minsize = 1000000
maxsize = 0

for i in Allsamplesize:
    if i > maxsize:
        maxsize = i
    if i < minsize:
        minsize = i

start = minsize - 500
end = maxsize + 500
edge = []
while start <= end:
    edge.append(start)
    start = start+2000

plt.hist(Allsamplesize, bins = edge, edgecolor='b', rwidth= 0.8)
if len(Timeoutseed) > 0:
    plt.axvline(Timeoutsize, color = 'r')
plt.savefig("State "+ State +" - Sample Size Graph.png")
plt.show()





