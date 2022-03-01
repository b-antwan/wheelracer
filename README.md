# Visnu Wheel
Ce TP a pour but d'analyser un flux vidéo (webcam ou fichier) pour extraire un angle.

Avec l'interface graphique, l'utilisateur peut choisir les couleurs à utiliser en guise de volant.
Les couleurs utilisent le system de Hue Saturation Value, et les valeurs chargées par défaut sont adaptées à la vidéo *wheel_racing.avi*.

Le programme génère un input pyton-uinput, capable d'être utilisé comme la vidéo d'exemple. Voici la **[Démonstration](https://youtu.be/k-DJnH6z9As)**

## Prérequis et dépendences
### Prérequis
Pour utiliser ce programme, il faut avoir:
- **python3**
- **[poetry](https://github.com/python-poetry/poetry)**
- **[tkinter](https://docs.python.org/3/library/tkinter.html#module-tkinter)**

### Dépendences
Pour installer les dépendences, il faut se rendre dans le dossier *projet/*, puis utiliser les commandes suivantes pour lancer un shell poetry et installer les dépendences:
```
$ poetry shell
$ poetry install
```

### Uinput
Ce projet envoie l'angle calculé comme uinput, pour pouvoir l'utiliser il faut s'assurer que l'utilisateur qui utilise le programme ait les droits d'écriture/lécture sur /dev/uinput

Si ce n'est pas encore le cas, cela peut être fait de la manière suivante:
```
$ sudo groupadd uinput

$ sudo usermod -a G uinput "$USER"

$ sudo chgrp uinput /dev/uinput

$ sudo chmod g+rw /dev/uinput
```

Cela va créer un groupe "uinput", ajouter l'utilisateur dedans, et donner les droits pour /dev/uinput.

## Utilisation du programme
Le programme peut utiliser le flux vidéo d'une webcam, ainsi qu'utiliser le flux vidéo d'un fichier vidéo.
Pour lancer le programme il faut etre dans dans le dossier *projet/* et utiliser les commandes suivantes:

Si on n'est pas dans le shell poetry, il faut d'abord faire:
```
$ poetry shell
```
Dès qu'on est dans le shell poetry on peut lancer le programme avec un fichier:
```
$ python visnu_wheel/wheelracer.py chemin/vers/fichier/video
```

**Si un chemin n'est pas fourni, le flux vidéo va être pris de la webcam.**

Pour sauvegarder le fichier des angles, le programme va demander le chemin, si aucun chemin n'est fourni, les angles ne vont pas être sauvegarés.

## Problèmes connus
Comme le programme génère le python-uinput, il utilise un thread que je n'ai pas pu "join" correctement.
Il faut donc faire un (ou deux) Ctrl-C à la fin du programme.