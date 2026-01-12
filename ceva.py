import itertools
from collections import Counter

    
values = [1,2,4, 3,4]

counts = Counter(values)
counts_vals = counts.most_common()

print(counts, counts_vals)