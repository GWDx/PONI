import os
import sys

targetFiles = [
    "Allensville", "Beechwood", "Marstons", "Benevolence", "Merom", "Coffeen", "Mifflinburg", "Newfields", "Onaga",
    "Cosmos", "Pinesdale", "Pomaria", "Forkland", "Ranchester", "Hanson", "Shelbyville", "Hiteman", "Stockman",
    "Klickitat", "Tolstoy", "Lakeville", "Wainscott", "Leonardo", "Lindenwood", "Woodbine", "Darden", "Collierville",
    "Markleeville", "Wiconisco", "Corozal "
]

files = os.listdir('data/semantic_maps/gibson/fmm_dists_123')

print("Files in the directory: ", files)

# split('_')[0]
# remove duplicates
splitFiles = [x.split('_')[0] for x in files]
result = set(splitFiles)

target = set(targetFiles)

print("Files in the directory: ", result)
print("Target files: ", target)

print("result - target: ", result - target)
print("target - result: ", target - result)
