# Bilingual Alignment

We will try to align the words of a text and its translation.


In order to launch the interface please execute the following command : run example_gui
in Ipython or any python interpreter.


Le code définissant la DTW se trouve dans mvc.py

Pour la classification morphologique, il a deux modules : 

radixtrie.py : définition du trie et du patricia trie
goldsmith.py : définition de la méthode de classification morphologique. 
functions.py :  définition de différents fonctions utilisées dans le module goldsmith. 
                ( quick_sort pour les dictionnaires etc...)


save_data :

Pour l'interface :

mvc.py : architecture model - view - controller
widgets.py : définition des widgets
virtual_mvc.py, interface.py : outils pour l'interface


Pour lancer l'interface : exécuter run example_gui.py 


Les autres fichiers à savoir : 
example_main_mvc.py : exemple d'utilisation de l'architecture mvc
GUI_test1.py ; GUI_test2.py : test de l'interface, n'a aucun impact sur le reste du code.


mvcpy.uml ; virtual_mvc.uml ; widgets.uml : définition des diagrammes uml utilisés dans  le rapport.