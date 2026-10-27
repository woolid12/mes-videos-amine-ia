# (start of visual slot in source seconds, end of slot, voice-over text)
# pronunciation hints are applied in tts.py: Aplevia -> Aplévia, bengkung -> benkoung
SEGMENTS = [
    (0.00, 3.36, "Il y a une chose que personne ne t'a dite après ta césarienne."),
    (3.44, 6.70, "Même si tu fais tout bien : sport, régime, rééducation…"),
    (6.76, 9.08, "ton ventre peut ne jamais redevenir comme avant."),
    (9.14, 10.82, "Et ce n'est pas un manque de volonté."),
    (10.88, 13.06, "La grossesse écarte les muscles du ventre."),
    (13.12, 16.28, "Et la cicatrice de césarienne, bien souvent, adhère à la peau."),
    (16.34, 20.56, "Ce n'est donc pas du gras, mais la peau du ventre qui retombe sur la cicatrice."),
    (20.62, 22.72, "C'est ce qu'on appelle le tablier de césarienne."),
    (22.78, 26.78, "Et ni le sport, ni les régimes, ni les gaines classiques ne peuvent régler ça."),
    (26.84, 28.00, "Alors, la solution ?"),
    (28.02, 34.12, "Il faut une compression douce et enveloppante, pour laisser au ventre le temps de se remettre en place et aux muscles de se resserrer."),
    (34.18, 37.90, "Tu savais qu'en Malaisie, les femmes ont rarement ce problème après l'accouchement ?"),
    (37.92, 41.70, "Depuis des siècles, elles enveloppent leur ventre dans un long tissu croisé."),
    (41.76, 44.36, "C'est le bengkung, une tradition ancestrale."),
    (44.42, 48.30, "Le souci, c'est que c'est long à mettre et pas du tout pratique au quotidien."),
    (48.36, 54.58, "Alors la marque suisse Aplevia te propose des culottes de compression croisée, directement inspirées de cette technique."),
    (54.64, 58.70, "Tu l'enfiles comme une culotte classique, et ton ventre est lissé instantanément."),
    (58.76, 61.52, "Contrairement aux gaines, la compression reste douce."),
    (61.58, 64.90, "Le but, c'est de maintenir le ventre en place, pas de l'écraser."),
    (64.96, 67.70, "Tu peux à nouveau porter tous les vêtements que tu aimes."),
    (67.76, 73.30, "Et jour après jour, tu te sens soutenue, à l'aise, et enfin bien dans ta peau."),
    (73.36, 75.78, "Et tu peux la porter même des années après l'accouchement."),
]
# the closing lines run longer than the original ending, so they get their own new timeline (see build.py)
OUTRO = [
    "Plus de 1000 clientes satisfaites l'ont notée 5 étoiles.",
    "En ce moment, c'est 2 achetées = 1 offerte, et la livraison est gratuite en Suisse.",
    "En plus, tu as 30 jours de garantie satisfaite ou remboursée, alors n'hésite pas !",
    "Clique sur « En savoir plus ».",
]
