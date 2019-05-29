import sys
from urllib.request import urlopen
from urllib.error import URLError
import json
import numpy as np
import matplotlib.pylab as plt
import scipy.ndimage as ndi

# command line usage <command> <redditor> <record type> <number>
# python ss.py Vyrnie comment 100

# grid_side_len = length of the sides of the grid; Default 90
# xfactor = passed to interval length (secs) and hash marks; actually plotting xfactor*log10; Default 10
grid_side_len=90
xfactor=10

# username = redditor username
# recordtype = 'submission' or 'comment';passed to pushshift and used in plot titles
# number = number of records requested; minimum of 3 to get one data point, max of 1000 from single pushshift query
# query_string = pushshift query string
username = sys.argv[1]
recordtype = sys.argv[2]
number = sys.argv[3]
query_string = 'https://api.pushshift.io/reddit/search/'+recordtype+'/?author='+username+'&sort=dsc&size='+number

print("username: " + username)
print("recordtype: " + recordtype)
print("number: " + number)
print("query: " + query_string)

# in case my internet goes down again
try:
    response = urlopen(query_string)
except URLError as err:
    print(err)
    exit(1)

# read json data dictionary
data = json.load(response)["data"]
print('# records: ' + str(len(data)))

# loop through records extracting UTC dates
# time_arr = []
# for i in range(len(data)): time_arr.append(data[i]["created_utc"])
time_arr = np.array([[data[i]["created_utc"]] for i in range(len(data))])

# subtract the previous event UTC timestamp from the current event
# these are the differential time intervals between events in seconds
# the range starts at 1 because there are is one less interval than there are data points
diff_arr = np.array([time_arr[i]-time_arr[i-1] for i in range(1, len(time_arr))])

# it happened a few times that differential times were zero
# can't take log of zero so just catch and store 1 instead
# pushshift gave us dates in descending order so subtraction yielded negative values
# take absolute value for differental intervals
diff_arr[diff_arr == 0] = -1
diff_arr[diff_arr < 0] *= -1

# x coordinates are from the first diff to end - 1
# y coordinates are from the second diff to the end
x_heat = diff_arr[:-1]
y_heat = diff_arr[1:]
x_heat_log = (np.log10(x_heat) * xfactor).astype(int)
y_heat_log = (np.log10(y_heat) * xfactor).astype(int)

# define heat map grid populated with zeros
# populate heat map for each element increment it's square by one
H = np.zeros((grid_side_len,grid_side_len))
for i in range(len(x_heat)):
    H[x_heat_log[i], y_heat_log[i]] += 1

# apply gaussian blur 0 is raw, higher numbers lead to higher smoothing
# also transpose so that the orientation is the same as the scatter plot
filter_strength = 2
H = ndi.gaussian_filter(H,filter_strength).transpose()

# giving a bit of padding for the image here
plt.xlim((-1, grid_side_len))
plt.ylim((-1, grid_side_len))

# calcuate tick marks and labels spaced 10 units apart
xfactor = 10
t_arr=[1*xfactor,2.079*xfactor,2.982*xfactor,4.033*xfactor,4.936*xfactor,5.977*xfactor,6.997*xfactor,7.975*xfactor]
t_label=['10sec','2min','16min','3hr','1day','11day','115day','3yr']

# make pretty
plt.xticks(t_arr, t_label, rotation='vertical')
plt.yticks(t_arr, t_label)
plt.title(username +' last '+str(len(time_arr))+' '+recordtype+'s')
plt.xlabel('Time before '+ recordtype)
plt.ylabel('Time after '+ recordtype, rotation='vertical')

# show plot
plt.imshow(H,cmap='nipy_spectral')
plt.show()