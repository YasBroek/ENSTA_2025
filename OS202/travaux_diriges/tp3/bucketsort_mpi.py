from mpi4py import MPI
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

def main():
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    numBuckets = 10
    arraySize = 24

    if rank == 0:
        tableau = np.random.rand(arraySize)
        print("Original array:", tableau)
    else:
        tableau = None

    localSize = arraySize // size
    localArray = np.empty(localSize, dtype=np.float64)
    comm.Scatter(tableau, localArray, root=0)

    localSorted = np.array(bucketSort(localArray.tolist(), numBuckets), dtype=np.float64)

    if rank == 0:
        gatheredSorted = np.empty(arraySize, dtype=np.float64)
    else:
        gatheredSorted = None

    localSize = len(localSorted)
    comm.Gather(localSorted, gatheredSorted, root=0)

    if rank == 0:
        print("Sorted array:", gatheredSorted)

if __name__ == "__main__":
    main()