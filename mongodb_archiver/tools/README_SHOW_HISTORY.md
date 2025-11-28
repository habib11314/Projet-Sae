show_history.sh - usage

Le script `show_history.sh` agrège les historiques de plusieurs shells (bash, zsh, fish, PowerShell) et permet de filtrer/limiter la sortie.

Exemples:
  # Afficher les 100 dernières commandes (défaut)
  ./tools/show_history.sh

  # Afficher les 50 dernières commandes contenant "git"
  ./tools/show_history.sh -n 50 -g git

  # Afficher en ordre du plus ancien au plus récent
  ./tools/show_history.sh -r

Notes:
- Sur Windows, exécutez le script depuis Git Bash ou WSL pour accéder aux chemins POSIX.
- Le script cherche les fichiers d'historique communs (~/.bash_history, ~/.zsh_history, fish, PowerShell). Si aucun fichier n'est trouvé, il échoue avec une erreur.
- Le script ne modifie pas les fichiers d'histoire.
