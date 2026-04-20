# Prospect Intelligence — Cottesloe

Outil interne de scoring et prospection immobilière pour les Western Suburbs de Perth, WA.

## Comment ça marche

1. Exporter les données de vente depuis RPData/CoreLogic (CSV)
2. Lancer le script de scoring Python pour générer `data/prospects_data.json`
3. Ouvrir `index.html` dans un navigateur

## Scoring

| Critère | Points |
|---|---|
| Holding 5–8 ans | +3 |
| Holding 8–12 ans | +4 |
| Holding 12–20 ans | +5 |
| Holding 20–30 ans | +4 |
| Holding 30+ ans | +3 |
| Maison individuelle | +1 |
| Plus-value > 200% | +3 |
| Plus-value > 100% | +2 |
| Achat creux Perth 2010–2016 | +1 |

## Stack

- Frontend : HTML/CSS/JS vanilla
- Données : JSON généré depuis RPData CSV via Python
- Lettres IA : Claude API (Sonnet)

## Prochaines étapes

- [ ] Multi-suburb support
- [ ] Serveur Flask pour éviter le fichier JSON statique
- [ ] Export Excel des prospects filtrés
- [ ] Intégration CRM (Homepass/Vaultre)
