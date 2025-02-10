import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from multiprocessing import Pool, cpu_count

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

def compute_convergence(args):
    mandelbrot_set, width, height, scaleX, scaleY, y_start, y_end = args
    convergence = np.empty((width, y_end - y_start), dtype=np.double)
    for y in range(y_start, y_end):
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            convergence[x, y - y_start] = mandelbrot_set.convergence(c, smooth=True)
    return convergence, y_start, y_end

def get_weighted_chunks(height, nbp):
    """Répartition pondérée des lignes en fonction de leur complexité estimée."""
    chunks = []
    center = height // 2
    for i in range(nbp):
        if i < nbp // 2:
            # Régions extérieures (moins coûteuses) : plus de lignes
            y_start = i * (height // nbp) * 2
            y_end = (i + 1) * (height // nbp) * 2
        else:
            # Régions centrales (plus coûteuses) : moins de lignes
            y_start = center - (height // (2 * nbp)) * (nbp - i)
            y_end = center + (height // (2 * nbp)) * (nbp - i)
        y_start = max(0, min(y_start, height))
        y_end = max(0, min(y_end, height))
        chunks.append((y_start, y_end))
    return chunks

def compute_line_difficulty(mandelbrot_set, width, scaleX, scaleY, y_start, y_end):
    difficulties = []
    for y in range(y_start, y_end):
        total_iterations = 0
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            total_iterations += mandelbrot_set.count_iterations(c, smooth=True)
        avg_difficulty = total_iterations / width
        difficulties.append((avg_difficulty, y))
    return difficulties

def main():
    mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
    width, height = 1024, 1024
    scaleX = 3./width
    scaleY = 2.25/height

    nbp = 2  # Nombre de processus disponibles
    chunk_size = height // nbp  # Taille de chaque bloc de lignes
    
    # Calculer la difficulté de chaque ligne
    difficulty = []
    for i in range(0, height, chunk_size):
        difficulty.extend(compute_line_difficulty(mandelbrot_set, width, scaleX, scaleY, i, min(i + chunk_size, height)))

    # Trier les lignes par difficulté (plus difficile en haut)
    difficulty.sort(key=lambda x: x[0], reverse=True)

    # Répartir les lignes entre les processus
    tasks = []
    for i in range(nbp):
        y_start = i * chunk_size
        y_end = (i + 1) * chunk_size
        tasks.append((mandelbrot_set, width, height, scaleX, scaleY, y_start, y_end))

    deb = time()
    with Pool(processes=nbp) as pool:
        results = pool.map(compute_convergence, tasks)

    convergence = np.empty((width, height), dtype=np.double)
    for result in results:
        conv, y_start, y_end = result
        convergence[:, y_start:y_end] = conv

    fin = time()
    print(f"Temps du calcul de l'ensemble de Mandelbrot : {fin-deb}")

    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.save("mandelbrot_mpi2.png")
    image.show()


if __name__ == "__main__":
    main()