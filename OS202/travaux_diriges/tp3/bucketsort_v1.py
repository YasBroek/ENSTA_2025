from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbproc = 4

nb_data_loc = 40  # nombre de données
data_loc = np.random.rand(nb_data_loc)
data_loc.sort()

min_local = data_loc[0]
max_local = data_loc[-1]

min_global = comm.allreduce(min_local, op=MPI.MIN)
max_global = comm.allreduce(max_local, op=MPI.MAX)

buckets = np.linspace( min_global, max_global, nbproc+1)
my_bucket = buckets[rank:rank+2]

send_counts = np.zeros(nbproc, dtype=int)  
for i in range(nbproc):
    send_counts[i] = np.sum((data_loc >= buckets[i]) & (data_loc < buckets[i + 1]))

sendbuf = []
for i in range(nbproc):
    mask = (data_loc >= buckets[i]) & (data_loc < buckets[i + 1])
    sendbuf.extend(data_loc[mask])
sendbuf = np.array(sendbuf, dtype=np.float64)

recv_counts = comm.alltoall(send_counts) 
recvbuf = np.empty(np.sum(recv_counts), dtype=np.float64)  

comm.Alltoallv(
    [sendbuf, send_counts, None, MPI.DOUBLE], 
    [recvbuf, recv_counts, None, MPI.DOUBLE]  
)

recvbuf.sort()

print(f"Process {rank}: my_bucket = {my_bucket}, recvbuf = {recvbuf}")

all_recvbuf = comm.gather(recvbuf, root=0)

if rank == 0:
    consolidated_list = np.concatenate(all_recvbuf)
    print("Consolidated sorted list:", consolidated_list)