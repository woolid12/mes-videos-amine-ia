# Aplevia "trahison / Sofia": (shots used, voice-over line). Shot k = [CUTS[k], CUTS[k+1]) in the source. 'card' = rebuilt offer card.
CUTS = [0, 3.86667, 7.73333, 11.1, 15.4333, 18.9, 22.7667, 25.7333, 26.6333, 30.6667, 33.6, 34.5333, 40.8, 44.4667, 48.4,
        52.1667, 56.1333, 58.1, 59.5667, 60.1333, 62.4667, 63.9667, 67.6667, 71.5667, 74.4333, 75.6667, 79.5333, 83.4667,
        90.3, 93.2333, 94.3, 98.1667, 102.033, 104.567, 105.967, 109.833, 114.8, 117.8, 118.933, 122.8, 126.8, 130.567,
        135.467, 140.867, 144.6, 147.433, 148.233, 152.133, 156.133, 160.1, 167.1]
MIRROR = {0, 1, 3, 4}          # first four shots of the edit
LABEL_SHOTS = {34}             # erase the "SEMAINE 6" label (JOUR 1 on shot 28 is kept)
SEGMENTS = [
    ([0, 1], "Mon mari m'a trompée six mois après notre deuxième bébé. Avec une collègue de 29 ans."),
    ([3], "Il n'a même pas nié. D'après lui, c'est moi qui avais changé."),
    ([4, 5], "Pourtant, j'avais perdu mes kilos. Il ne restait que ce petit ventre autour du nombril."),
    ([6, 7], "Abdos, kiné, régimes… rien ne changeait."),
    ([9, 10], "Et mon mari est parti s'installer chez elle."),
    ([12, 13], "Puis mon amie Sofia est venue de Malaisie. Trois enfants, et un ventre plus plat que le mien."),
    ([14, 15], "Elle m'a vue rentrer le ventre devant le miroir, et elle a sorti un long tissu : le bengkung."),
    ([16, 19, 20], "En Malaisie, les femmes enveloppent leur taille dans un tissu croisé, serré devant et sur les côtés."),
    ([23, 24], "Mais le bengkung, c'est une demi-heure à nouer. Et sous un jean, ça ne tient pas."),
    ([25, 26], "Alors elle m'a montré sa culotte, croisée en X comme le bengkung : devant, sur les côtés et dans le dos."),
    ([27], "Elle s'appelle Aplevia. Sofia m'en a laissé une avant de repartir."),
    ([28, 29, 30], "Le premier jour, mon ventre était maintenu. Le soir, je l'avais oubliée : rien qui gratte, rien qui roule."),
    ([34, 35], "Un jour, j'ai ressorti ma robe. Dans le miroir, je me suis souri, pour la première fois depuis longtemps."),
    ([36, 38], "Aux quatre ans de notre fils, au parc, il est venu avec elle. Il s'est arrêté net."),
    ([39, 40, 41], "Elle s'est approchée : « Ton ventre… tu as fait quoi ? » J'ai souri : « C'est une culotte. Aplevia. »"),
    ([42], "Le soir, il m'a écrit : « Tu étais belle. » Je n'ai pas répondu. Moi aussi, je me trouvais belle."),
    ([43, 44], "Aplevia : des bandes croisées en X, un maintien à 360 degrés. Notée 5 étoiles par plus de 1000 clientes satisfaites."),
    (['card'], "En ce moment, c'est 2 achetées = 1 offerte, avec la livraison gratuite en Suisse. Et tu as 30 jours pour l'essayer : satisfaite ou remboursée."),
    ([49], "Clique sur « En savoir plus ». Parce que toi aussi, tu as le droit de te regarder comme ça."),
]
OUTRO = []
