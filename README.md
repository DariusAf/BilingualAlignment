# Bilingual Alignment

We try to automatically align the words of a text and its translation, based on their vector of apparition.

In order to launch the interface please execute main.py.

The interface relies on the **PyQT4** cross-platform. 

## Pour la DTW :

* *mvc.py* : l'algorithme d'alignement est entièrement contenu dans la partie modèle

## Pour la classification morphologique, il a deux modules : 

* *radixtrie.py* : définition du trie et du patricia trie
* *goldsmith.py* : définition de la méthode de classification morphologique. 
* *functions.py* :  définition de différents fonctions utilisées dans le module goldsmith. 
                ( quick_sort pour les dictionnaires etc...)

## Pour l'interface :

*virtual_mvc.py* : architecture générique model - view - controller
*mvc.py* : contient la DTW et les éléments de codes pour l'alignement
*widgets.py* : définition des widgets de l'interface

## Les autres fichiers :

* *main.py* : utilisation avec interface du modèle.
