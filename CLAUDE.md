# Mes vidéos Amine – réglages par défaut

Adaptation de pubs vidéo concurrentes pour le produit **RongiVex** (marque **aplevia**), marché francophone (Suisse, CHF).

## À appliquer à chaque nouvelle vidéo (sauf indication contraire)
- **Sous-titres d'origine** : effacés (ProPainter sur Replicate, masque issu de l'OCR, plan par plan, `fp16: true`).
- **Filtre** « dark night » à 5 %.
- **Miroir** sur les 10 premières secondes, prolongé jusqu'à la fin du plan en cours.
- **Musique** : supprimée (voix off seule).
- **Voix off** : Kev (ElevenLabs `jGpnMdbhtKgQbVrYezOx`), modèle `eleven_multilingual_v2`, vitesse 1.15–1.2, stabilité 0.3–0.4, style 0.5–0.6. Ton commercial et chaleureux, tutoiement.
- **Anti-écho** : toujours passer la voix off finale dans `lucataco/resemble-enhance` (`denoise_flag: true`) et garder la sortie **débruitée** (« version A », `output-denoised.wav`).
- **Vérification de la voix** : transcrire chaque phrase (Groq whisper-large-v3) et refaire uniquement les phrases ratées. Points sensibles connus : « RongiVex », « Ta famille n'a plus peur » (dit « n'en a »), verbes en -ent prononcés -ant.
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

## Coûts de repère
- Effacement sous-titres : ~0.05 $ par plan (Replicate).
- Retouche d'image (nano-banana) : ~0.04 $ ; animation Kling 5 s : ~0.35 $.
- Replicate limite à 6 créations/min : ne jamais relancer une création sans vérifier qu'elle n'existe pas déjà (doublons facturés).
