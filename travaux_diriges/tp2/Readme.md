# TD n° 2 - 27 Janvier 2025

##  1. Parallélisation ensemble de Mandelbrot

L'ensensemble de Mandebrot est un ensemble fractal inventé par Benoit Mandelbrot permettant d'étudier la convergence ou la rapidité de divergence dans le plan complexe de la suite récursive suivante :
$$
\left\{
\begin{array}{l}
    c\,\,\textrm{valeurs\,\,complexe\,\,donnée}\\
    z_{0} = 0 \\
    z_{n+1} = z_{n}^{2} + c
}\end{array}
\right.
$$
dépendant du paramètre $c$.

Il est facile de montrer que si il existe un $N$ tel que $\mid z_{N} \mid > 2$, alors la suite $z_{n}$ diverge. Cette propriété est très utile pour arrêter le calcul de la suite puisqu'on aura détecter que la suite a divergé. La rapidité de divergence est le plus petit $N$ trouvé pour la suite tel que $\mid z_{N} \mid > 2$.

On fixe un nombre d'itérations maximal $N_{\textrm{max}}$. Si jusqu'à cette itération, aucune valeur de $z_{N}$ ne dépasse en module 2, on considère que la suite converge.

L'ensemble de Mandelbrot sur le plan complexe est l'ensemble des valeurs de $c$ pour lesquels la suite converge.

Pour l'affichage de cette suite, on calcule une image de $W\times H$ pixels telle qu'à chaque pixel $(p_{i},p_{j})$, de l'espace image, on associe une valeur complexe  $c = x_{min} + p_{i}.\frac{x_{\textrm{max}}-x_{\textrm{min}}}{W} + i.\left(y_{\textrm{min}} + p_{j}.\frac{y_{\textrm{max}}-y_{\textrm{min}}}{H}\right)$. Pour chacune des valeurs $c$ associées à chaque pixel, on teste si la suite converge ou diverge.

- Si la suite converge, on affiche le pixel correspondant en noir
- Si la suite diverge, on affiche le pixel avec une couleur correspondant à la rapidité de divergence.

1. À partir du code séquentiel `mandelbrot.py`, faire une partition équitable par bloc suivant les lignes de l'image pour distribuer le calcul sur `nbp` processus  puis rassembler l'image sur le processus zéro pour la sauvegarder. Calculer le temps d'exécution pour différents nombre de tâches et calculer le speedup. Comment interpréter les résultats obtenus ?

pour nbp = 1 (sequetiel):
    Temps du calcul de l'ensemble de Mandelbrot : 2.510436534881592
    Temps de constitution de l'image : 0.03764939308166504
pour nbp = 2:
    Temps du calcul de l'ensemble de Mandelbrot : 1.58333420753479
    Temps de constitution de l'image : 0.03587222099304199
    Speedup (pour le temps de calcul): 2.51/1.58 = 1.59 (Speedup sous-lineaire -> nbp > speedup)
pour nbp = 4:
    Temps du calcul de l'ensemble de Mandelbrot : 1.207521915435791
    Temps de constitution de l'image : 0.03989124298095703
    Speedup (pour le temps de calcul): 2.51/1.21 = 2.07 (Speedup sous-lineaire -> nbp > speedup)


2. Réfléchissez à une meilleur répartition statique des lignes au vu de l'ensemble obtenu sur notre exemple et mettez la en œuvre. Calculer le temps d'exécution pour différents nombre de tâches et calculer le speedup et comparez avec l'ancienne répartition. Quel problème pourrait se poser avec une telle stratégie ?

Une répartition statique améliorée pourrait être basée sur la répartition des lignes de manière non uniforme, selon la difficulté estimée de chaque ligne. Pour ce faire, on peut calculer une estimation de la "difficulté" de chaque ligne en calculant la convergence moyenne des pixels de cette ligne, et donc créer un tableau où chaque ligne est associée à une valeur représentant sa difficulté, et finalement attribuer les lignes aux processus.

Les resultats obtenus sont:
pour nbp = 2:
    Temps du calcul de l'ensemble de Mandelbrot : 1.624197006225586
    Temps de constitution de l'image : 0.03592252731323242
    Speedup (pour le temps de calcul): 2.51/1.62 = 1.55
pour nbp = 4:
    Temps du calcul de l'ensemble de Mandelbrot : 1.1569476127624512
    Temps de constitution de l'image : 0.031923770904541016
    Speedup (pour le temps de calcul): 2.51/1.16 = 2.16

On voit que cette répartition obtient des valeurs plus petits pour le speedup. Pourtant, cette strategie pourrait poser des problèmes suivants: déséquilibre de la charge, effet de bord de la parallélisation ou mémoire partagée (si le nombre de processus devient trop élevé, il pourrait y avoir une pression sur la mémoire partagée et les caches, ce qui pourrait ralentir les calculs)

3. Mettre en œuvre une stratégie maître-esclave pour distribuer les différentes lignes de l'image à calculer. Calculer le speedup avec cette approche et comparez  avec les solutions différentes. Qu'en concluez-vous ?

Les resultats obtenus sont:
pour nbp = 2:
    Temps du calcul de l'ensemble de Mandelbrot : 1.5587713718414307
    Temps de constitution de l'image : 0.03760123252868652
    Speedup (pour le temps de calcul): 2.51/1.56 = 1.61
pour nbp = 4:
    Temps du calcul de l'ensemble de Mandelbrot : 1.124225378036499
    Temps de constitution de l'image : 0.03648066520690918
    Speedup (pour le temps de calcul): 2.51/1.12 = 2.24

On voit que le speedup est encore amelioré. Cet exercice nous montre que le parallélisme peut être efficace lorsqu’il est bien géré, mais aussi qu’il doit être utilisé de manière réfléchie. Le choix de la stratégie, le nombre de processus, et la gestion de la communication et des données sont tous des facteurs clés dans la maximisation des performances.

## 2. Produit matrice-vecteur

On considère le produit d'une matrice carrée $A$ de dimension $N$ par un vecteur $u$ de même dimension dans $\mathbb{R}$. La matrice est constituée des cœfficients définis par $A_{ij} = (i+j) \mod N$. 

Par soucis de simplification, on supposera $N$ divisible par le nombre de tâches `nbp` exécutées.

### a - Produit parallèle matrice-vecteur par colonne

Afin de paralléliser le produit matrice–vecteur, on décide dans un premier temps de partitionner la matrice par un découpage par bloc de colonnes. Chaque tâche contiendra $N_{\textrm{loc}}$ colonnes de la matrice. 

- Calculer en fonction du nombre de tâches la valeur de Nloc

Nloc = dim/nbp

- Paralléliser le code séquentiel `matvec.py` en veillant à ce que chaque tâche n’assemble que la partie de la matrice utile à sa somme partielle du produit matrice-vecteur. On s’assurera que toutes les tâches à la fin du programme contiennent le vecteur résultat complet.
- Calculer le speed-up obtenu avec une telle approche

Temps sequentiel: 0.006043672561645508 secondes
Temps avec parallelisation (colonnes): 0.00315093994140625 secondes
Speedup: 1,92

### b - Produit parallèle matrice-vecteur par ligne

Afin de paralléliser le produit matrice–vecteur, on décide dans un deuxième temps de partitionner la matrice par un découpage par bloc de lignes. Chaque tâche contiendra $N_{\textrm{loc}}$ lignes de la matrice.

- Calculer en fonction du nombre de tâches la valeur de Nloc

Nloc = dim/nbp

- paralléliser le code séquentiel `matvec.py` en veillant à ce que chaque tâche n’assemble que la partie de la matrice utile à son produit matrice-vecteur partiel. On s’assurera que toutes les tâches à la fin du programme contiennent le vecteur résultat complet.
- Calculer le speed-up obtenu avec une telle approche

Temps sequentiel: 0.006043672561645508 secondes
Temps avec parallelisation (lignes): 0.0028684139251708984 secondes
Speedup: 2,10

## 3. Entraînement pour l'examen écrit

Alice a parallélisé en partie un code sur machine à mémoire distribuée. Pour un jeu de données spécifiques, elle remarque que la partie qu’elle exécute en parallèle représente en temps de traitement 90% du temps d’exécution du programme en séquentiel.

En utilisant la loi d’Amdhal, pouvez-vous prédire l’accélération maximale que pourra obtenir Alice avec son code (en considérant n ≫ 1) ?

À votre avis, pour ce jeu de donné spécifique, quel nombre de nœuds de calcul semble-t-il raisonnable de prendre pour ne pas trop gaspiller de ressources CPU ?

En effectuant son cacul sur son calculateur, Alice s’aperçoit qu’elle obtient une accélération maximale de quatre en augmentant le nombre de nœuds de calcul pour son jeu spécifique de données.

En doublant la quantité de donnée à traiter, et en supposant la complexité de l’algorithme parallèle linéaire, quelle accélération maximale peut espérer Alice en utilisant la loi de Gustafson ?

Réponse:
La loi d'Amdhal nous donne:
S(n) = t_s/(f*t_s+((1-f)*t_s)/n)
pour n >> 1, S(n) ~ 1/f
pour f = 1 - 0.9 = 0.1: S(n) = 1/0.1 = 10 
L'accélération maximale que peut obtenir Alice avec son code est 10.

Pour une accélération de 90% du maximum, par exemple:
S(n) = 9 = n/(1+(n-1)*f) -> n = 81
Donc, 81 nœuds semblent être un choix raisonnable pour obtenir environ 90% de l’accélération maximale sans surutilisation des ressources CPU.

En utilisant la loi de Gustafson:
S(n) = n + (1-n)*t_s
Pour la quantité initiale de données:
4 = n + (1-n)*0.1 -> n = 4.33 ~ 4
Lorsque la quantité de données double, la complexité de l’algorithme parallèle étant linéaire, on peut supposer qu’il faut également doubler le nombre de nœuds. Donc, n' = 8
S(n) = 8 + (1-8)*0.1 = 7.33