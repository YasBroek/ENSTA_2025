from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbproc = 4

nb_data_loc = 40  # nombre de données
data_loc = np.random.rand(nb_data_loc)

if rank <= nbproc - 2:
    data_loc = data_loc**4  

data_loc.sort()

all_data = comm.gather(data_loc, root=0)

if rank == 0:
    all_data = np.concatenate(all_data)
    buckets = np.quantile(all_data, np.linspace(0, 1, nbproc + 1))
else:
    buckets = np.empty(nbproc + 1, dtype=np.float64)

comm.Bcast(buckets, root=0)

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

all_recvbuf = comm.gather(recvbuf, root=0)

if rank == 0:
    consolidated_list = np.concatenate(all_recvbuf)
    print("Consolidated sorted list:", consolidated_list)