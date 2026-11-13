# Mes vidéos Amine – réglages par défaut

Adaptation de pubs vidéo concurrentes pour le produit **RongiVex** (marque **aplevia**), marché francophone (Suisse, CHF).

## À appliquer à chaque nouvelle vidéo (sauf indication contraire)
- **Sous-titres d'origine** : effacés (ProPainter sur Replicate, masque issu de l'OCR, plan par plan, `fp16: true`).
- **Filtre** « dark night » à 5 %.
- **Miroir** sur les 10 premières secondes, prolongé jusqu'à la fin du plan en cours.
- **Musique** : supprimée (voix off seule).
- **Voix off** : Corentin (ElevenLabs `IHngRooVccHyPqB4uQkG`, « Corentin - Enthusiastic and Bright »), modèle `eleven_multilingual_v2`, vitesse 1.15, stabilité 0.4, style 0.5. Ton commercial et chaleureux, tutoiement. Alternative : Kev (`jGpnMdbhtKgQbVrYezOx`). Autres voix FR masculines du compte : Marcel, Hugo, Raphael (Nicolas = ton journaliste, à éviter).
- **Anti-écho** : toujours passer la voix off finale dans `lucataco/resemble-enhance` (`denoise_flag: true`) et garder la sortie **débruitée** (« version A », `output-denoised.wav`).
- **Vérification de la voix** : transcrire chaque phrase (Groq whisper-large-v3) et refaire uniquement les phrases ratées. Points sensibles connus : « RongiVex », « Ta famille n'a plus peur » (dit « n'en a »), verbes en -ent prononcés -ant : écrire le texte envoyé à la voix au singulier phonétique (« vivent » → « vive », « passent » → « passe ») et rétablir l'orthographe dans les sous-titres.
- **Sous-titres FR** : texte noir sur cases blanches arrondies (Inter SemiBold 42 px), placés sur la position des anciens sous-titres pour masquer les traces d'effacement.

## Produit et offre
- Visuels : paquet noir RongiVex (aplevia), 12 sachets.
- Ingrédients réels : menthe poivrée, cannelle, bois de cèdre, huile de ricin (jamais de clou de girofle).
- Offre : 2 achetés, le 3e offert (36 sachets / 3 paquets, CHF 66.00 au lieu de CHF 99.00), livraison gratuite, satisfait ou remboursé 30 jours.
- Ne pas reprendre les promesses chiffrées des concurrents (durée en jours, surface couverte, prix en $) sans validation.

## Plans RongiVex déjà générés (à réutiliser avant de générer)
- `rongivex-aplevia/assets/` : plan produit animé (cuisine), plan produit intro (arc), animation des 4 ingrédients.
- `video2/assets/` : mains qui tiennent le paquet (jardin), homme au camping-car, paquet sur la table, sachet de graines sorti du paquet, plan cannelle.
- `video3/assets/` : femme à genoux dans le jardin avec le paquet.
- `video5/assets/` : mains qui tiennent le paquet en intérieur (4 plans), ingrédients avec cèdre.
- Plans nettoyés (logo/sous-titres effacés) réutilisables : sachets dans une main, sous l'évier, derrière le frigo, cellier, tapis, fumée verte (vidéos 4 à 7) ; pommes de pin = bois de cèdre, huile versée dans un bécher = huile de ricin (vidéo 4).

## Montage
- Son : assembler la voix off en Python/numpy (pas de graphe ffmpeg avec 30 `atrim` sur la même entrée : blocage).
- Plans de ProPainter : sortis en 30 i/s quel que soit le fichier d'origine.
- Fichiers > 100 Mo refusés par GitHub : réencoder si besoin.

## Coûts de repère
- Effacement sous-titres : ~0.05 $ par plan (Replicate).
- Retouche d'image (nano-banana) : ~0.04 $ ; animation Kling 5 s : ~0.35 $.
- Replicate limite à 6 créations/min : ne jamais relancer une création sans vérifier qu'elle n'existe pas déjà (doublons facturés).
