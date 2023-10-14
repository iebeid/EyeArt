import numpy as np
data = [1,1,1,2,2,2,3,3,3,3]
groups = [1,2,3]
# groups = np.array([0,1,2])
#
# unique_groups = np.unique(groups)
# sums = []
# for group in unique_groups:
#     sums.append(data[groups == group].sum())
#
# print(sums)

def count_group(data,group):
    group_counter = 0
    for d in data:
        if d == group:
            group_counter = group_counter + 1
    return group_counter

def tabulate(data,groups):
    sums = []
    for group in groups:
        sum = count_group(data,group)
        sums.append(sum)
    return sums

sums = tabulate(data,groups)
print(sums)

# for group in unique_groups: