Certaines transactions arrivent d'une manière régulière comme les salaires, les factures, le loyer, les paiements de prêts, etc.. Celles-ci sont appropriées pour les **récurrences**. Certains revenus et dépenses peuvent seulement être estimés, comme l'épicerie, l'habillement, resto, etc.. C'est alors le temps pour des **budgets**. Avec les fonctionnalités de récurrence et de budget dans moneyGuru, vous pouvez faire des prévisions sur votre situation financière.

Comment ça marche
-----

Les récurrences et les budgets fonctionnent avec un système d'"occurrences". Quand vous créez une récurrence ou un budget (dans les vues Récurrences et Budgets), vous créez en fait une transaction "modèle". À partir de ce modèle, des occurrences sont ajoutées dans les vues Transactions et Compte pour chaque date à laquelle le modèle est exécuté (avec un icône ![](images/clock.png)). Par exemple, si vous créez une récurrence mensuelle, vous n'aurez qu'un seul modèle dans la vue Récurrences, mais vous aurez une occurrence de ce modèle chaque mois dans les vues Transactions et Compte.

Les occurrences ne sont pas statiques. Elles peuvent être modifiées individuellement si besoin est (si, par exemple, votre salaire est plus élevé à un moment donné). Quand vous modifiez une occurrence, moneyGuru vous demandera quelle est la portée de votre modification. En effet, si vous voulez, vous pouvez affecter toutes les futures occurrences en une seule modification (si, par exemple, votre loyer a augmenté).

Quand vous modifiez une transaction modèle, vous modifiez toutes les occurrences *excepté* pour les occurrences modifiées individuellement.

Les occurrences de budgets sont un peu différentes. Elle ne peuvent pas être modifiées, mais leur montant est affecté par les transactions se trouvant dans les dates que le budget couvre et affectant le compte auquel le budget est assigné. Par exemple, si vous avez un budget mensuel de 100$ pour "Vêtements", une transaction en juillet de 20$ dans "Vêtements" changerait l'occurrence du 31 juillet de ce budget à 80$.

Aussi, les occurrences de budgets peuvent seulement être dans le future. Ces occurrences disparaissent à partir du moment où leur date est atteinte.

Créer une récurrence
-----

Pour créer une récurrence, utilisez la vue Récurrence et cliquez sur "Nouvelle récurrence". Un dialogue de détails apparaîtra. Ce dialogue est similaire au dialogue de transaction, mais contient des champs particuliers vous permettant de spécifier la fréquence des occurrences.

Il est aussi possible de créer une récurrence à partir d'une transaction modèle. Ajoutez simplement une transaction normale, puis cliquez sur "Créer une récurrence à partir de la sélection". Une nouvelle récurrence sera crée avec les détails de la transaction, il ne vous suffit plus que de spécifier la fréquence.

Modifier une récurrence
-----

En plus de pouvoir modifier votre récurrence modèle dans la vue Récurrences, vous pouvez aussi modifier les occurrences individuelles. Elles se modifient comme n'importe quelle transaction, mais vous pouvez modifier la portée de vos modifications avec la touche Shift.

* **Modifier une seule occurrence:** Si vous modifiez une occurrence normalement, seulement cette occurrence sera modifiée.
* **Modifier toutes les occurrences futures:** Si vous tenez Shift au moment où vous terminez votre modification, celle-ci s'appliquera à toutes les occurrences futures.
* **Passer une occurrence:** Si vous voulez exceptionnellement enlever une occurrence sans enlever les occurrences futures, vous pouvez simplement supprimer celle-ci comme vous le feriez avec une transaction.
* **Arrêter une récurrence:** Pour arrêter une récurrence à partir d'une certaine date, supprimez l'occurrence qui arrive après la dernière tout en tenant Shift.

Le concept est simple: Vous modifiez vos occurrences comme vous le faites avec une transaction, mais si vous tenez Shift, la portée est globale.

Budgets
-----

Un budget peut être créé dans la vue Budgets. Les options de répétition sont les mêmes que pour les récurrences. Le champ Compte est le compte ciblé par le budget et le champ Cible est le champ dans lequel le budget "prend" son argent. Si par exemple vous utilisez votre compte courant comme cible, c'est ce compte dont la balance sera diminuée ou augmentée dans les graphes. Notez que d'avoir une cible ne change *pas* la façon dont les transactions affectent les comptes avec budgets. Même si votre budget a comme cible votre compte courant, les dépense faites avec votre carte de crédit seront comptabilisées dans le budget.

Intégration à Cashculator
-----

**Cette fonctionnalité requière Cashculator v1.2.2 ou plus récent.**

Les budgets et récurrences dans moneyGuru sont bien si vous savez déjà quel budget vous voulez adopter. Par contre, moneyGuru ne permet pas vraiment d'expérimenter avec des budgets hypothétiques afin de designer le budget le plus approprié. Il existe une application d'un autre développeur qui se spécialise dans le design de budgets: [Cashculator](http://www.apparentsoft.com/cashculator).

moneyGuru peut exporter vos données vers Cashculator afin de vous permettre de designer vos budgets encore plus facilement. Pour utiliser cette fonctionnalité, suivez ces instructions:

1. Téléchargez Cashculator et démarrez le au moins une fois (moneyGuru a besoin de la structure principale de sa base de donnée). Ensuite, quittez Cashculator.
2. Ouvrez votre document moneyGuru, ouvrez un nouvel onglet, puis cliquez sur le bouton "Cashculator".
3. L'onglet montrera une liste de vos compte de revenus et dépenses. Avec cette liste, vous devez indiquez quels comptes sont récurrents et lesquels ne le sont pas. Cette distinction est importante dans Cashculator.
4. Cliquez sur "Exporter". Vos compes seront exportés ainsi que les statistiques de revenus et dépenses de vos compte pour les 4 derniers mois. Ne vous inquiétez pas si vous avez déjà des données dans Cashculator. moneyGuru utilise une copie séparée de la base de donnée principale et laisse l'originale intouchée.
5. Assurez vous que Cashculator est fermé, puis cliquez sur "Ouvrir Cashculator". Casuculator sera alors ouvert avec la base de donnée de moneyGuru (c'est pourquoi il faut utiliser ce bouton, autrement Cashculator s'ouvre sur sa propre base de donnée).
6. Dans Cashculator, il y aura un scénario appellé "moneyGuru". C'est ce scénario qui contient vos donnée. Utilisez le pour faire le design de votre budget (veuillez vous référer à la documentation de Cashculator pour cela).
7. Ensuite, vous pouvez recréer les budgets de Cashculator dans moneyGuru. Il faut le faire manuellement, mais c'est une limitation temporaire.
8. Cashculator retournera en mode normal (avec sa base de donnée régulière) lorsque vous quitterez moneyGuru.

**Pour tout de suite, seule la fonctionnalité d'exportation est disponible.** La façon de fonctionner de Cashculator est très différente de celle de moneyGuru. Pour l'exportation de donnée, ça va encore, mais pour une importation automatique de budgets à partir des données de Cashculator, les choses se corsent. Il y a plusieurs façon de remplir les cellules "Plan" dans Cashculator et il n'est pas évident de définir une procédure d'importation claire.

Cette fonctionnalité est toute neuve (v2.1) et ce que je veux faire c'est de tester la chose un peu. Si vous utiliser l'exportation vers Cashculator, veuillez me laisser savoir comment vous faites vos budgets et comment vous pensez que l'information que vous mettez dans Cashculator devrait être transférée dans moneyGuru. Veuillez me faire part de tout ça sur [le forum de support](http://getsatisfaction.com/hardcodedsoftware). Merci!