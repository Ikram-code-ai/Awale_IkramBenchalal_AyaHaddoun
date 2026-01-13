# Projet Awalé - Intelligence Artificielle

## Auteurs
- **Ikram BENCHALAL**
- **Aya HADDOUN**

Master 1 Informatique - Parcours Intelligence Artificielle  
Université Côte d'Azur - 2025/2026

## Description
Bot IA pour le jeu d'Awalé (variante colorée avec 16 trous et graines R/B/T).

Algorithme : **Minimax + Alpha-Beta + Iterative Deepening**

## Fichiers
- `player.exe` : Exécutable du bot (prêt à l'emploi)
- `Arbitre.java` : Arbitre pour lancer les matchs
- `awale_game/` : Code source Python
  - `bot.py` : Intelligence artificielle
  - `game.py` : Moteur du jeu
  - `player_adapter.py` : Interface de communication
  - `main.py` : Tests locaux

## Utilisation
```bash
javac Arbitre.java
java Arbitre
```

## Résultat
Match contre Kacem : **43-44** (défaite d'1 point)
