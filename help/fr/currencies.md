moneyGuru a support solide pour la gestion des devises multiples. Chaque montant, quel qu'il soit, est d'une devise particulière. Tout montant que vous tapez peut être de n'importe laquelle devise. Beaucoup d'effort ont été déployés dans moneyGuru pour être sûr que l'information de devise soit claire sans être envahissante. Il suffit de connaître les règles de base.

Il y a deux types de devises dans moneyGuru. La devise **native** et les devises **étrangères**. La devise native est déterminée par vos préférences système (dans "International"). Les devises étrangères sont toutes les autres.

L'affichage de ces devises suit une règle très simple: Si un montant est de votre devise native, ce montant est laissé tel quel. Si il est d'une devise étrangère, le code ISO (USD, CAD, EUR, GBP, etc..) correspondant à cette devise est ajouté au montant.

Pour ce qui est de l'entrée de donnée, dans presque tous les cas, entrer un montant sans spécifier une devise produira un montant de votre devise native. La seule exception est le cas où vous êtes dans la vue Compte d'un compte en devise étrangère. Un montant entré sans devise sera alors de la devise du **compte**. Dans **tous** les cas, un montant entrée avec un code ISO de cette devise (exemple, "24.12 EUR") sera de cette même devise.

Quand les montants dans un compte ne sont pas de la même devise que ce compte, le taux de change de ce jour est utilisé pour calculer la balance du compte. Il est impossible de réconcilier une entrée n'ayant pas la même devise que le compte. Lors de la réconciliation, changez ce montant pour le montant que votre banque vous charge avant de réconcilier.

Transactions à devises multiples
-----

La grande majorité des transactions que vous faites impliquent seulement une devise à la fois. Même si vous achetez quelque chose en devise étrangère avec votre carte de crédit, la transaction restera toujours une seule devise à la fois (elle sera d'abord en devise étrangère, puis vous la convertirez en devise native lors de votre réconciliation).

Mais il y a certaines transactions qui nécessitent des entrées de devises différentes au sein de la même transaction. Ces transactions sont les transactions de transfert entre deux actifs ou passifs de devise différente (par exemple, un transfert d'argent entre un compte EUR et un compte USD). 

Cette situation est problématique car il n'y a aucun moyen de balancer une telle transaction vu que les taux de change ne sont que des estimés. Ainsi, dans ces cas exceptionnels, **la transaction balance toujours**. Ainsi, vous pouvez avoir une transaction de 100 USD d'un côté et de 80 EUR de l'autre qui balance.

Pour créer une telle transaction, passez simplement par le dialogue de détails de transaction et modifiez les entrées de cette transaction à souhait. Lorsque cette transaction deviendra multi-devise, vous verrez que le bouton "Balancer les devises" sera disponible. Ce bouton permet d'utiliser le taux de change actuel pour créer une nouvelle entrée correspondant à la différence entre le taux de change que vous avez obtenu et le taux de change en vigueur à cette date. Ça peut être utile si vous voulez compter les taux "préférentiels" que la banque se donne (elle se donne souvent 1% ou 2% en sa faveur) comme une dépense.

Les règles en bref
-----

* Les montants en devises étrangères ont **toujours** un code ISO explicite.
* Taper explicitement un code ISO avec un montant produit **toujours** un montant de cette devise.
* Taper un montant sans code produit un montant de votre devise native, sauf quand ce montant est tapé dans une vue Compte d'une compte étranger.
* La valeur nette et les profits sont calculés en devise native.
* Une transaction impliquant plus qu'une devise balance toujours.

Devises supportées
-----

* [USD] U.S. dollar
* [EUR] European Euro
* [GBP] U.K. pound sterling
* [CAD] Canadian dollar
* [AUD] Australian dollar
* [JPY] Japanese yen
* [INR] Indian rupee
* [NZD] New Zealand dollar
* [CHF] Swiss franc
* [ZAR] South African rand
* [AED] U.A.E. dirham
* [ANG] Neth. Antilles flori
* [ARS] Argentine peso
* [ATS] Austrian schillin
* [BBD] Barbadian dollar
* [BEF] Belgian franc
* [BHD] Bahraini dinar
* [BRL] Brazilian real
* [BSD] Bahamian dollar
* [CLP] Chilean peso
* [CNY] Chinese renminbi
* [COP] Colombian peso
* [CZK] Czech Republic koruna
* [DEM] German deutsche mark
* [DKK] Danish krone
* [EGP] Egyptian pound
* [ESP] Spanish peseta
* [FIM] Finnish mark
* [FJD] Fiji dollar
* [FRF] French franc
* [GHC] Ghanaian
* [GHS] Ghanaian cedi (new)
* [GRD] Greek drach
* [GTQ] Guatemalan quetzal
* [HKD] Hong Kong dollar
* [HNL] Honduran lempira
* [HRK] Croatian kuna
* [HUF] Hungarian forint
* [IDR] Indonesian rupiah
* [IEP] Irish pound
* [ILS] Israeli new shekel
* [ISK] Icelandic krona
* [ITL] Italian lira
* [JMD] Jamaican dollar
* [KRW] South Korean won
* [LKR] Sri Lanka rupee
* [LTL] Lithuanian litas
* [MAD] Moroccan dirham
* [MMK] Myanmar (Burma) kyat
* [MXN] Mexican peso
* [MYR] Malaysian ringgit
* [NLG] Netherlands guild
* [NOK] Norwegian krone
* [PAB] Panamanian balboa
* [PEN] Peruvian new sol
* [PHP] Philippine peso
* [PKR] Pakistan rupee
* [PLN] Polish zloty
* [PTE] Portuguese escudo
* [RON] Romanian new leu
* [RSD] Serbian dinar
* [RUB] Russian rouble
* [SEK] Swedish krona
* [SGD] Singapore dollar
* [SIT] Slovenian tolar
* [SKK] Slovak koruna
* [THB] Thai baht
* [TND] Tunisian dinar
* [TRL] Turkish lira
* [TWD] Taiwanese new dollar
* [UAH] Ukrainian hryvnia
* [VEB] Venezuelan bolivar
* [VEF] Venezuelan bolivar fuerte
* [VND] Vietnamese dong
* [XAF] CFA franc
* [XCD] East Caribbean dollar
* [XPF] CFP franc
