# Outils de montage (scripts de référence)

Scripts utilisés pour les vidéos 1 à 12. Les chemins (`S=/tmp/...scratchpad`, `V=S+'/vXX'`) et les numéros de plans sont à adapter pour chaque nouvelle vidéo.

| Script | Rôle |
|---|---|
| `rep.py` | Client Replicate (upload, prédiction, téléchargement, anti-doublons) |
| `ocr.py` | OCR de 1 image sur 3 (RapidOCR) → `mask/ocr_3.json` |
| `mkmask.py` | Repérage des sous-titres/logos → `mask/events.json` + vidéo masque |
| `inpaint.py` | Effacement plan par plan avec ProPainter (Replicate) |
| `build_remplacements.py` | Remplacement de plans par la bibliothèque + miroir 10 s + dark night 5 % |
| `gen_voix.py` | Génération de la voix off (ElevenLabs, voix Corentin) avec horodatage |
| `verif_voix.py` | Vérification phrase par phrase par transcription (Groq) |
| `build_voix_soustitres.py` | Calage de la voix sur les plans (numpy), sous-titres, montage final |

Méthode de travail détaillée : voir `CLAUDE.md` à la racine.
