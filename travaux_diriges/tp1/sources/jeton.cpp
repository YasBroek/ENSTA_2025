#include <iostream>
#include <mpi.h>

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    MPI_Comm globComm;
    MPI_Comm_dup(MPI_COMM_WORLD, &globComm);
    int rank, nbp;

    MPI_Comm_rank(globComm, &rank);
    MPI_Comm_size(globComm, &nbp);

    int jeton = 0;
    int tag = 100;
    MPI_Status status;

    if (rank == 0) {
        jeton = 1;
        MPI_Send(&jeton, 1, MPI_INT, rank + 1, tag, globComm);
        MPI_Recv(&jeton, 1, MPI_INT, nbp - 1, tag, globComm, &status);
        std::cout << "Processus " << rank << " a reçu le jeton final : " << jeton << std::endl;
    } else {
        MPI_Recv(&jeton, 1, MPI_INT, rank - 1, tag, globComm, &status);
        jeton++;
        MPI_Send(&jeton, 1, MPI_INT, (rank + 1) % nbp, tag, globComm);
        std::cout << "Processus " << rank << " a envoyé le jeton avec valeur : " << jeton << std::endl;
    }

    MPI_Finalize();
    return EXIT_SUCCESS;
}
