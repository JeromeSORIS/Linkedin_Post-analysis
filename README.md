# Linkedin_Post-analysis
* Inspiré par : https://github.com/Ollie-Boyd/Linkedin-post-timestamp-extractor
* Réalisé dans un but pédagogique.

### Objectifs
Code Python permettant :
* de récupérer l'heure UTC de publication :
  * d'un post Linkedin,
  * de sa mise à jour,
  * du re-post
  * et de tous les commentaires 
* l'URL en clair de la vidéo
* les profils des membres qui ont interagi
* l'URL avec la meilleure définition des images et logos
* ...

### Mode d'emploi
1. Dans le navigateur, ouvrir le post Linkedin à analyser

![alt text](https://github.com/JeromeSORIS/Linkedin_Post-analysis/blob/main/linkedin_1.png)

3. Sélectionner une partie du texte du post (copier) et lancer également l'inspecteur (F12)
4. Dans l'inspecteur, rechercher le texte copié précédemment et copier l'entiereté du dictionnaire

![alt text](https://github.com/JeromeSORIS/Linkedin_Post-analysis/blob/main/linkedin_2.png)

6. Enregistrer le dictionnaire dans le fichier texte (exemple : linkedin_data.txt)
7. Exécuter le fichier python dans le même dossier que le fichier .txt
8. Un fichier .json (linkedin_json.json par défaut) se crée avec l'ensemble des éléments (à visualiser dans un navigateur)

![alt text](https://github.com/JeromeSORIS/Linkedin_Post-analysis/blob/main/linkedin_3.png)

### Nota
![alt text](https://github.com/JeromeSORIS/Linkedin_Post-analysis/blob/main/meme.jpg)
... Normalement :)
