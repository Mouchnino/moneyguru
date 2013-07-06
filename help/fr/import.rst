Importer vos données
====================

moneyGuru peut importer les formats QIF, OFX, QFX et CSV. Pour importer un fichier, cliquez sur "Importer..." et choisissez un fichier à importer. La fenêtre d'importation apparaîtra:

|import_window|

Il y a un onglet pour chaque compte présent dans le fichier importé. Vérifiez que les données que vous voulez importer ont du sens, décochez les lignes que vous ne voulez pas importer, puis cliquez sur Importer pour importer le compte sélectionné.

Arranger les dates
------------------

moneyGuru détermine le format de date des fichiers automatiquement. La plupart du temps, c'est sans problème. Mais des fois, les dates sont ambiguës et il se peut que moneyGuru ne choisisse pas le bon format de date. Si vous voyez que vos dates ne sont pas correctes, vous pouvez interchanger les champs des dates. Si par exemple les mois sont à la place des jours et vice versa, vous pouvez utiliser la fonction "Jour <--> Mois". Si vous cochez "Appliquer à tous", le changement sera appliqué à tout les comptes.

Arranger les descriptions et provenances
----------------------------------------

Il arrive qu'un fichier mal généré par une autre application se trompe de champ et que vous ayez ainsi les champs Description et Tiers interchangés. Vous n'avez qu'à utiliser la fonction "Description <--> Tiers" pour régler tout ça.

.. todo:: Update the 2 section below with the new "Fix broken fields" section.

Importer dans un compte existant
--------------------------------

Si le fichier importé provient d'une banque, il est bien possible que vous vouliez l'importer dans un compte déjà existant. Pour ce faire, choisissez ce compte dans Compte Cible. Vous aurez alors a jumeler les transactions des deux comptes ensemble. En effet, il est tout à fait possible que votre fichier importé contienne des transactions déjà présentes dans votre document. La table se transformera en table à deux côté comme celle là:

|import_match_table|

Du côté gauche, il y a toutes les transactions **non-réconciliées** présentes dans votre compte. Du côté droit, il y a les transactions à importer. Il faut alors jumeler les transactions identiques. Vous pouvez le faire en glissant l'une sur l'autre. Vous pouvez aussi dé-jumeler des transactions en cliquant sur leur petit cadenas.

Importation CSV
---------------

L'importation des fichiers CSV fonctionne comme avec les autres fichiers, mais il faut passer par une étape intermédiaire dans laquelle vous devez définir la signification des colonnes de votre CSV:

|import_csv_options|

Le problème avec CSV c'est qu'il n'y a aucun standard. Cette fenêtre permet de dire à moneyGuru comment interpréter le fichier. D'abord, regardez les données affichées et déterminez quelle colonne fait quoi. Cliquez sur une colonne pour pouvoir déterminer son type. Les colonnes Date et Montant sont obligatoires.

Les fichiers CSV ont souvent des entêtes et des commentaires de fin de fichiers qui peuvent confondre moneyGuru. Décochez leur colonne "Imp." pour ne pas les importer.

Des fois, les fichiers sont si bizarres qu'il est difficile de déterminer le séparateur de champs. Si les données sont toutes prises dans la même colonne, identifiez le séparateur correct, entrez le dans "Séparateur" puis appuyez sur "Rescanner".

moneyGuru a la capacité de retenir vos configuration pour une importation ultérieure. Quand vous avez fini de configurer la fenêtre, sauvegardez la configuration. Vous pourrez la ramener lors de votre prochaine importation.

.. |import_window| image:: image/import_window.png
.. |import_match_table| image:: image/import_match_table.png
.. |import_csv_options| image:: image/import_csv_options.png
