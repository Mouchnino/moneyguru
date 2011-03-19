Concepts de base
================

moneyGuru est basé sur la `comptabilité en partie double <http://fr.wikipedia.org/wiki/Comptabilité_en_partie_double>`__. Au centre de ce système se trouve la **transaction** qui représente un mouvement d'argent d'un ou plusieurs comptes vers un ou plusieurs autres comptes à une date précise. Une transaction consiste en un ensemble balancé de deux entrées ou plus, chacune affectant un compte. N'importe quel compte, quelque soit son type, peut envoyer de l'argent à n'importe quel autre compte. Ça peut devenir utile dans des cas comme la :doc:`gestion de liquidités <cash>`. Le système central de moneyGuru n'est pas bien plus compliqué que ça. Quand les devises s'en mêlent, certains nouvelles règles s'appliquent, mais ces règles sont décrite dans la :doc:`page sur les devises <currencies>`.

Onglets et vues
---------------

La gestion de vos documents moneyGuru se fait à l'aide des différentes vues disponibles dans l'application, les principales étant décrites ci-dessous. Ces vues sont gérées à l'aide d'onglets. Ces onglets s'utilisent de la même façon que dans n'importe quelle autre application à onglets. Vous créez un onglet avec |cmd|\ T, vous le fermez avec |cmd|\ W et vous y naviguez avec |cmd_shift|\ ←→. Quand vous ouvrez un compte avec |basics_show_account_arrow|, un nouvel onglet est créé pour ce compte.

L'intervalle de dates
---------------------

L'intervalle de dates sélectionné affecte l'application entière. Tout ce que vous voyez dans les vues est en rapport avec l'intervalle sélectionné. Par exemple, si Août 2008 est sélectionné, tout ce que vous voyez dans toutes les vues sera entre 2008/08/01 et 2008/08/31. L'intervalle de date est controllé par ce truc:

|basics_date_range|

Il y a 7 types d'intervalle:

#. **Mois:** Commence au premier jour d'un mois et se termine au dernier jour de celui-ci.
#. **Trimestre:** Commence au premier jour d'un trimestre et se termine au dernier jour de celui-ci.
#. **Année:** Commence au premier jour d'une année et se termine au dernier jour de celle-ci.
#. **Année courante:** Commence au premier jour de l'année *courante* et ce termine *aujourd'hui*.
#. **Année flottante:** Un intervalle annuel qui *suit* la date d'aujourd'hui. Il dure *un an* mais utilise la préférence "nombre de mois flottants" pour déterminer quand dans le futur l'intervalle doit arrêter.
#. **Toutes les transactions:** Commence à la première transaction et se termine a "aujourd'hui + mois flottants".
#. **Personnalisé:** Permet de choisir de dates précises d'intervalle.

Lorsqu'un intervalle "navigable" est sélectionné (Mois, Trimestre, Année), les flèches peuvent être utilisée pour naviguer dans le temps (sur le clavier, c'est |cmd_opt|\ [ et |cmd_opt|\ ]). Il y a aussi des raccourcis clavier pour les types d'intervalle aux mêmes (|cmd_opt|\ 1-7). |cmd_opt|\ T ramène l'intervalle à aujourd'hui.

Pour les intervalles personnalisés, il est possible de sauvegarder ces intervalles dans une des 3 cases disponibles afin de les ré-invoquer plus tard.

La mince ligne rouge
--------------------

Toute l'information dans moneyGuru est affichée selon l'intervalle courant. Les choses deviennent intéressantes quand cet intervalle se termine dans le futur. Si vous avez des récurrences ou des budgets, les chiffres et les graphes que vous allez voir seront en fonction de ces prédictions. Dans les graphes, il y a une nette différence entre le passé et le future grâce à un ligne rouge verticale. Ce qui est à gauche est le passé, ce qui est à droite est le futur.

Valeur nette et Profits/Pertes
------------------------------

|basics_net_worth|

Les vues "Valeur nette" et "Profits/Pertes" sont là où les comptes sont gérés et où il est possible d'avoir des statistiques générales sur votre situation financière. Les deux vues ont une configuration et un comportement similaires.

**Liste de comptes:** La liste de compte permet :doc:`d'ajouter, de modifier et de supprimer <editing>` vos comptes. Cette liste vous donne aussi les statistiques générales pour chaque compte, ainsi que les totaux correspondants.

**Show Account:** À côté de chaque compte, il y a un petit |basics_show_account_arrow|. Vous pouvez cliquer dessus pour ouvrir ce compte dans un nouvel onglet. Vous pouvez aussi appuyer sur |cmd|\ →.

**Account Exclusion:** Vous pouvez "exclure" des compte avec le petit |basics_account_out|, ou en pressant sur |cmd_shift|\ X. Les compte exclus ne comptent pas dans le totaux et dans le graphes.

**Diagrammes circulaires:** Les diagrammes circulaires représentent le poids relatif de vos comptes. Si vous avez de groupe de compte, le fait de fermer ce groupe dans la liste de compte va regrouper ces comptes dans le diagramme circulaire.

**Graphe:** Le graphe représente la progression de la statistique principale de la vue (valeur nette, profit) dans le temps.

**Colonnes:** Chaque liste de comptes a des colonnes différentes (personnalisable avec |cmd|\ J).

* **Valeur nette:**

    * **# Compte:** Un numéro optionnel lié au compte. Voir la :doc:`page sur les éditions <editing>` pour plus de détails.
    * **Début:** La balance du compte au début de l'intervalle. Les récurrences sont inclues, mais pas les budgets.
    * **Fin:** Balance du compte à la fin de l'intervalle.
    * **Variation:** La différence entre Début et Fin.
    * **Variation %:** Variation en terme de pourcentage.
    * **Budgeté:** Le montant total budgeté **restant** pour lequel le compte est une **cible**. Autrement dit, si votre budget reflète la réalité, votre balance à la fin de l'intervalle devrait être de Fin + Budgeté.

* **Profits/Pertes:**

    * **# Compte:** Même chose que dans la valeur nette.
    * **Courant:** Le montant total alloué à ce compte pendant l'intervalle (sans les budgets).
    * **Précédent:** Dans le cas des intervalles navigables, le montant total alloué lors de l'intervalle précédent. Pour les intervalles "Année courante" et "Année flottante", l'intervalle précédent est l'année précédente. Pour "Toutes les transactions", il n'y a pas d'intervalle précédent. Pour les intervalles personnalisés, l'intervalle précédent est de même durée que l'intervalle courant.
    * **Variation:** Même chose que dans la valeur nette.
    * **Budgeté:** Le montant budgeté restant à allouer à ce compte pour l'intervalle. Autrement, si votre budget reflète la réalité, le montant alloué au compte à la fin de l'intervalle devrait être Courant + Budgeté.

Transactions
------------

|basics_transactions|

La vue de Transactions contient toutes les transactions du document pour l'intervalle sélectionné. Depuis cette vue, vous pouvez :doc:`ajouter, modifier et supprimer <editing>` des transactions. Cette vue est la plus efficace si vous avez beaucoup de tranasctions à entrer (une pile de factures et reçus par exemple). La colonne **Montant** contient la valeur totale du mouvement d'argent. **De/Vers** contient le ou les comptes desquels et vers lesquels l'argent est transféré. Par exemple, si vous payez votre épicerie avec votre carte de débit, "De" serait "Compte Courant" et "Vers" serait "Nourriture".

Au dessus de la liste de transactions, il y a une barre de filtre permettant d'afficher seulement des transactions d'un certain type.

* **Revenu:** Montrer seulement les transactions affectant au moins un compte de revenu.
* **Dépense:** Montrer seulement les transactions affectant au moins un compte de dépense.
* **Transfert:** Montrer seulement les transactions affectant au moins deux comptes d'actifs ou passifs.
* **Non-assigné:** Montrer seulement les transactions ayant au moins une entrée sans compte assigné.
* **Reconcilié:** Montrer seulement les transactions ayant au moins une entrée réconciliée.
* **Non Reconcilié:** Montrer seulement les transactions n'ayant aucune entrée réconciliée.

Cette vue contient aussi des petits |basics_show_account_arrow| qui servent aussi à montrer le compte correspondant dans un nouvel onglet.

Compte
------

|basics_account|

Cette vue contient les transactions *de la perspective d'un compte spécifique*. Chaque ligne, au lieu de représenter la transaction en entier, représente **l'entrée** au sein de la transaction qui affecte le compte sélectionné. Vous pouvez ouvrir cette vue en cliquant sur |basics_show_account_arrow| dans les autres vues. Les informations contenues dans cette vue sont semblable à celle de la vue Transactions, excepté pour ce qui est des comptes et des montants. Dans la colonne "Transfert" est affiché les compte de l"autre côté" de la transaction. C'est-à-dire toutes les autres entrées de la transaction. La colonne "Montant" est séparée en deux colonnes, "Dépôt" et "Retrait", semblable au format des relevés bancaires. Si le compte sélectionné est une actif ou un passif, il y a aussi une colonne "Balance" qui donne la balance du compte après chaque entrée.

À l'instar de la vue Transactions, cette vue a une barre de filtres. Les filtres disponibles sont semblables, mais il y a quand même quelques différences.

* **Dépôt:** Montrer seulement les entrées dont le montant est un dépôt.
* **Retrait:** Montrer seulement les entrées dont le montant est un retrait.
* **Transfert:** Montrer seulement les entrée faisant partie d'une transaction affectant au moins deux comptes d'actifs ou passifs.
* **Non-assigné:** Montrer seulement les entrées non assignées.
* **Reconcilié:** Montrer seulement les entrées réconciliées.
* **Non-Réconcilié:** Montrer seulement les entrées non réconciliées.

Le bouton "Réconciliation" dans la barre de filtre sert à changer le mode de :doc:`réconciliation <reconciliation>` (seulement pour les compte d'actifs et de passifs)

Comme partout ailleurs, le petit |basics_show_account_arrow| sert a ouvrir le compte correspondant. Une particularité de cette vue par contre est que l'usage répété de cette flèche pour la même transaction garantie l'ordre d'ouverture. Ça veut dire que cette flèche peut être utilisée pour "cycler" au travers de toutes les entrées d'une transaction.

La table d'entrée commence la plupart du temps par une entrée "Balance précédente". Cette entrée, à l'instar des extraits bancaires, indique la balance du compte au début de l'intervalle de date sélectionné.

Grand Livre
-----------

Cette vue met tout les comptes ensemble en montre leurs entrées respectives. La façon dont ces entrées sont présentées est pratiquement identique à la vue Compte. Cette vue est surtout la pour faire des rapports.

Filtre
------

Le champ "Filtre" dans la barre d'outils sert a chercher vos transactions avec des requêtes textuelles. Lorsque vous entrez du texte dans ce champ, seulement les transaction contenant ce texte dans un de leurs champs (description, provenance, etc.) seront visibles. Vous pouvez chercher pour des comptes ou des groupes spécifique avec "account: compte1,compte2" ou "group: groupe1,groupe2". Très utile pour les :doc:`modifications multiples <editing>`.

Options de visibilité
---------------------

|basics_view_options|

moneyGuru a une fenêtre controllant la visibilité de certaines colonnes et des graphiques. Vous pouvez invoquer cette fenêtre avec |cmd|\ J.

Impression
----------

Dans moneyGuru, vous pouvez imprimer n'importe quelle vue. Vous voulez la liste de vos transactions de l'an passé? Ouvrez la bonne vue, ajustez l'intervalle, et appuyez sur |cmd|\ P. Voilà.