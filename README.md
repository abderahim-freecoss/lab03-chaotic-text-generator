# Générateur de texte chaotique — Lab 03

Banc d’essai Streamlit pour comparer un HMM à états POS simples, un HMM à états séparés par rôle et un générateur trigramme. Le projet montre les étiquettes, mesure la structure et la diversité, et permet d’étiqueter une phrase avec Viterbi.

## Installation et lancement

Exécuter les commandes depuis ce dossier :

```bash
python -m pip install -r requirements.txt
python -m src.evaluate
python -m src.evaluate_real
streamlit run app.py
```

Pour régénérer le rapport français d’une page après mise à jour des évaluations :

```bash
python report/generate_report.py
```

La première évaluation mesure le corpus synthétique. L’évaluation EWT télécharge les données Universal Dependencies English EWT lors de sa première exécution et nécessite une connexion Internet. Le corpus synthétique est déjà inclus dans `data/corpus.csv`.

## Déploiement

Pour Streamlit Community Cloud, publier ce dossier dans un dépôt GitHub, puis sélectionner `app.py` comme fichier principal. Garder `data/corpus.csv` et `requirements.txt` dans le dépôt. Les données EWT téléchargées (`data/ewt/`) ne sont pas requises par l’application et sont ignorées par Git.

## Résultats attendus et limites

Le modèle à états séparés par rôle atteint 100 % de séquences de tags valides sur ce petit corpus synthétique à T=1, tandis que le trigramme donne une meilleure plausibilité sujet-verbe mais peut mémoriser des phrases. Ces métriques sont propres à la grammaire synthétique et ne mesurent pas la qualité de l’anglais réel. La qualité de l’étiquetage est nettement plus faible sur le corpus EWT.

## Fichiers

- `app.py` : interface Streamlit et outils interactifs.
- `src/pipeline.py` : HMM, Viterbi, trigramme et métriques.
- `src/evaluate.py` : évaluation synthétique et graphique.
- `src/evaluate_real.py` : comparaison sur UD English EWT.
- `results/` : sorties calculées des évaluations.
- `report/farahi_abderahim_rapport_lab03.pdf` : rapport français avec résultats et captures d’écran de l’application.
- `screenshots/` : captures de l’application.
