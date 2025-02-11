import numpy as np

def bucketSort(array: list, numBuckets: int = 10):
    
    minVal, maxVal = min(array), max(array)
    
    rangeVal = maxVal - minVal
    normalizedArray = [(x - minVal) / rangeVal for x in array]

    buckets = [[] for _ in range(numBuckets)]
    for item in normalizedArray:
        bucketIndex = min(int(item * numBuckets), numBuckets - 1)
        buckets[bucketIndex].append(item)

    sortedArray = []
    for bucket in buckets:
        bucket.sort()
        sortedArray.extend([minVal + x * rangeVal for x in bucket])

    return sortedArray

tableau = np.random.rand(24)
print("Original array:", tableau)
sortedTableau = bucketSort(tableau)
print("Sorted array:", sortedTableau)