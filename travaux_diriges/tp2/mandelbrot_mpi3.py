import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from multiprocessing import Process, Queue, cpu_count

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius: float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth) / self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex, smooth=False) -> int | float:
        z: complex
        iter: int

        if c.real * c.real + c.imag * c.imag < 0.0625:
            return self.max_iterations
        if (c.real + 1) * (c.real + 1) + c.imag * c.imag < 0.0625:
            return self.max_iterations
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real - 0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5 * (1 - ct.real / max(ctnrm2, 1.E-14)):
                return self.max_iterations
        z = 0
        for iter in range(self.max_iterations):
            z = z * z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z))) / log(2)
                return iter
        return self.max_iterations

from multiprocessing import Pool

def compute_line(mandelbrot_set, width, scaleX, scaleY, y):
    convergence = np.empty(width, dtype=np.double)
    for x in range(width):
        c = complex(-2. + scaleX * x, -1.125 + scaleY * y)
        convergence[x] = mandelbrot_set.convergence(c, smooth=True)
    return convergence, y

def main():
    mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
    width, height = 1024, 1024
    scaleX = 3. / width
    scaleY = 2.25 / height

    nbp = 2  # Nombre de processus
    convergence = np.empty((width, height), dtype=np.double)

    deb = time()
    with Pool(processes=nbp) as pool:
        results = pool.starmap(compute_line, [(mandelbrot_set, width, scaleX, scaleY, y) for y in range(height)])

    for conv, y in results:
        convergence[:, y] = conv

    fin = time()
    print(f"Temps du calcul de l'ensemble de Mandelbrot : {fin-deb}")

    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T) * 255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.save("mandelbrot_pool.png")
    image.show()

if __name__ == "__main__":
    main()