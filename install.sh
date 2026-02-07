#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
REPO="https://github.com/anthonymarandon/telebot-claude-code.git"
INSTALL_DIR="$HOME/.telebot"
BIN_DIR="$HOME/.local/bin"
BIN_NAME="telebot"

# --- Couleurs ---
C='\033[36m'  # cyan
G='\033[32m'  # green
R='\033[31m'  # red
D='\033[2m'   # dim
N='\033[0m'   # reset
B='\033[1m'   # bold

info()  { printf "${C}::${N} %s\n" "$1"; }
ok()    { printf "${G}ok${N} %s\n" "$1"; }
fail()  { printf "${R}erreur${N} %s\n" "$1"; exit 1; }

# --- Banner ---
printf "${C}"
cat << 'EOF'

  ████████╗███████╗██╗     ███████╗██████╗  ██████╗ ████████╗
  ╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
     ██║   █████╗  ██║     █████╗  ██████╔╝██║   ██║   ██║
     ██║   ██╔══╝  ██║     ██╔══╝  ██╔══██╗██║   ██║   ██║
     ██║   ███████╗███████╗███████╗██████╔╝╚██████╔╝   ██║
     ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝  ╚═════╝    ╚═╝

EOF
printf "${D}              Installateur — Telegram Bot Claude Code${N}\n\n"

# --- Vérification des prérequis ---
info "Vérification des prérequis..."

# Python 3.10+
if command -v python3 &>/dev/null; then
    PY=$(command -v python3)
elif command -v python &>/dev/null; then
    PY=$(command -v python)
else
    fail "Python 3 introuvable. Installe Python 3.10+ avant de continuer."
fi

PY_VERSION=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PY -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PY -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    fail "Python $PY_VERSION détecté, 3.10+ requis."
fi
ok "Python $PY_VERSION ($PY)"

# git
if ! command -v git &>/dev/null; then
    fail "git introuvable. Installe git avant de continuer."
fi
ok "git $(git --version | awk '{print $3}')"

# tmux
if ! command -v tmux &>/dev/null; then
    printf "${R}attention${N} tmux introuvable — nécessaire pour piloter Claude Code.\n"
    printf "         Installe-le : ${D}brew install tmux${N} / ${D}apt install tmux${N}\n"
else
    ok "tmux $(tmux -V | awk '{print $2}')"
fi

echo ""

# --- Installation ---
if [ -d "$INSTALL_DIR" ]; then
    info "Dossier $INSTALL_DIR existant, mise à jour..."
    cd "$INSTALL_DIR"
    git pull --ff-only || fail "Impossible de mettre à jour. Vérifie l'état du repo."
    ok "Repo mis à jour"
else
    info "Clonage dans $INSTALL_DIR..."
    git clone "$REPO" "$INSTALL_DIR"
    ok "Repo cloné"
fi

cd "$INSTALL_DIR"

# --- Environnement virtuel ---
info "Configuration de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    $PY -m venv venv
    ok "venv créé"
else
    ok "venv existant"
fi

# --- Dépendances ---
info "Installation des dépendances..."
./venv/bin/pip install -q -r requirements.txt
ok "Dépendances installées"

echo ""

# --- Lien dans le PATH ---
info "Création de la commande ${B}$BIN_NAME${N}..."
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/$BIN_NAME" << WRAPPER
#!/usr/bin/env bash
exec "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/cli.py" "\$@"
WRAPPER
chmod +x "$BIN_DIR/$BIN_NAME"
ok "Commande installée dans $BIN_DIR/$BIN_NAME"

# Vérifier que BIN_DIR est dans le PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    printf "${R}attention${N} ${B}$BIN_DIR${N} n'est pas dans ton PATH.\n"
    printf "         Ajoute cette ligne à ton ${D}~/.bashrc${N} ou ${D}~/.zshrc${N} :\n"
    printf "\n         ${C}export PATH=\"\$HOME/.local/bin:\$PATH\"${N}\n"
fi

# --- Configuration ---
echo ""
if [ ! -f "$INSTALL_DIR/.env" ]; then
    info "Configuration initiale..."
    echo ""
    printf "  Token Telegram (BotFather) : "
    read -r TOKEN
    printf "  Ton User ID Telegram       : "
    read -r USER_ID
    cat > "$INSTALL_DIR/.env" << ENV
TELEGRAM_BOT_TOKEN=$TOKEN
ALLOWED_USER_ID=$USER_ID
ENV
    ok ".env configuré"
else
    ok ".env déjà présent, configuration conservée"
fi

# --- Terminé ---
echo ""
printf "${G}${B}Installation terminée !${N}\n\n"
printf "  Utilisation :\n"
printf "    ${C}telebot${N}          Menu interactif\n"
printf "    ${C}telebot start${N}    Démarrer le bot\n"
printf "    ${C}telebot stop${N}     Arrêter le bot\n"
printf "    ${C}telebot status${N}   Voir l'état\n"
printf "    ${C}telebot config${N}   Reconfigurer\n"
echo ""
