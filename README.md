# Wumpus_IA02

Projet IA02 jeu du Wumpus


Le but est de créer une intelligence artificielle capable de jouer au jeu du Wumpus.

## Lancement du programme
------------------------------

Pour lancer le programme il suffit d'ouvrir projet.py dans un interpreteur.
Pour changer la taille de la carte, dans Wumpus_client4, dans la classe mettre la taille en dur.

## Ce que fait le programme
-------------------------------

Le programme défini dans un premier temps des variables.
Ensuite le programme écrit toutes les clauses du jeu du Wumpus.

Dans un second temps, le programme va essayer d'obtenir toutes les informations sur le monde en un moindre coût.
Enfin, une fois chaque case déduite ou sondée, le programme va définir un chemin jusqu'a l'or s'il existe.
Puis pour finir le programme déplace le personnage sur le chemin trouvé pour collecter tous les Gold.
(Ne marche que pour la version serveur car lorsqu'on probe en local le joueur se déplace)