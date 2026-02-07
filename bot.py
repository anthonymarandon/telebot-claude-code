import asyncio
import html
import os
import subprocess
from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
SESSION_NAME = "claude"
_last_response = ""  # Dernière réponse extraite, pour éviter les doublons


def auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ALLOWED_USER_ID:
            await update.message.reply_text("Non autorisé.")
            return
        return await func(update, context)
    return wrapper


def run(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()


def session_exists() -> bool:
    return subprocess.run(
        f"tmux has-session -t {SESSION_NAME}", shell=True, capture_output=True
    ).returncode == 0


def _is_separator(line: str) -> bool:
    """Détecte un séparateur ──── (au moins 10 caractères ─)."""
    s = line.strip()
    return len(s) > 10 and all(c == "─" for c in s)


def _is_menu_option(line: str) -> bool:
    """Détecte une option de menu numérotée (❯ 1. Yes, 2. Non…)."""
    after = line.strip().lstrip("❯").strip()
    return bool(after) and after[0].isdigit() and "." in after.split()[0]


def _is_status_bar(line: str) -> bool:
    """Détecte la barre de statut (~ │ Opus 4.6 │ $0.12 │ ...)."""
    s = line.strip()
    return "│" in s and any(k in s for k in ("$", "Opus", "Sonnet", "Haiku"))


def _has_numbered_options(lines: list[str]) -> bool:
    """Vérifie si les lignes contiennent des options numérotées."""
    for line in lines:
        s = line.strip().lstrip("❯").strip()
        if s and s[0].isdigit() and len(s) > 1 and "." in s.split()[0]:
            return True
    return False


def _find_response_zone(lines: list[str]) -> tuple[int, int]:
    """Trouve la zone de réponse : (start, end) entre le prompt ❯ et le séparateur ────."""
    prompt_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if not (stripped.startswith("❯") and len(stripped) > 2):
            continue
        # Exclure les ❯ indentés (options de dialogue permission)
        if lines[i].lstrip() != lines[i]:
            continue
        # Exclure les options numérotées (❯ 1. Minimaliste, ❯ 2. Moderne…)
        if _is_menu_option(lines[i]):
            continue
        prompt_idx = i
        break
    if prompt_idx < 0:
        return (0, 0)
    start = prompt_idx + 1
    end = len(lines)
    for i in range(start, len(lines)):
        if _is_separator(lines[i]):
            end = i
            break
    return (start, end)


def extract_response(capture: str) -> str:
    """Extrait la dernière réponse de Claude depuis la capture du terminal."""
    lines = capture.splitlines()
    if not lines:
        return ""
    start, end = _find_response_zone(lines)
    if start >= end:
        return ""
    response_lines = []
    in_response = False
    for line in lines[start:end]:
        stripped = line.strip()
        if not stripped:
            if in_response:
                response_lines.append("")
            continue
        # Marqueur de réponse Claude ⏺
        if stripped.startswith(("⏺", "●")):
            in_response = True
            response_lines.append(stripped[1:].strip())
            continue
        # Contenu indenté après un ⏺ (continuation, ⎿ tool output, listes…)
        if in_response and (line.startswith("  ") or stripped.startswith("⎿")):
            response_lines.append(line.rstrip())
            continue
        # Ignorer le reste (spinners, activité, timing ✻…)
    return "\n".join(response_lines).strip()


def extract_dialog(capture: str) -> str:
    """Extrait un dialogue interactif (permission, AskUserQuestion, trust prompt…).

    Détecte les dialogues par la présence d'options numérotées sous le séparateur ────
    de fin de zone de réponse. Fonctionne pour :
    - Permission dialogs (❯ indenté, options numérotées)
    - AskUserQuestion (❯ colonne 0, barre d'onglets ☐/✔)
    - Trust prompt au démarrage (pas de zone de réponse)
    """
    lines = capture.splitlines()
    start, end = _find_response_zone(lines)

    # Trouver le premier séparateur ──── à/après la fin de la zone de réponse
    sep_idx = -1
    search_from = end if end > 0 else 0
    for i in range(search_from, len(lines)):
        if _is_separator(lines[i]):
            sep_idx = i
            break
    if sep_idx < 0:
        return ""

    # Collecter le contenu sous le séparateur jusqu'à la barre de statut
    below = []
    for i in range(sep_idx + 1, len(lines)):
        if _is_status_bar(lines[i]):
            break
        if lines[i].strip().startswith("⏵"):
            break
        below.append(lines[i])

    # Pas d'options numérotées → pas un dialogue
    if not _has_numbered_options(below):
        return ""

    # Formater : garder le contenu, ignorer les séparateurs ────
    dialog_lines = []
    for line in below:
        stripped = line.strip()
        if not stripped:
            if dialog_lines:
                dialog_lines.append("")
            continue
        if _is_separator(line):
            continue
        dialog_lines.append(stripped)
    return "\n".join(dialog_lines).strip()


def is_claude_done(output: str) -> bool:
    """Vérifie si Claude a fini de répondre (⏺ présent, pas de spinner, pas de dialogue)."""
    lines = output.splitlines()
    start, end = _find_response_zone(lines)
    if start >= end:
        return False
    has_response = False
    for i in range(start, end):
        stripped = lines[i].strip()
        if stripped.startswith(("⏺", "●")):
            has_response = True
        if "…" in stripped and not stripped.startswith(("⏺", "●")):
            return False
    return has_response


def compute_diff(old: str, new: str) -> str:
    """Calcule la partie nouvelle de new par rapport à old."""
    if not old:
        return new
    if new == old:
        return ""
    if new.startswith(old):
        return new[len(old):].strip()
    # Recherche par lignes : trouver où le contenu déjà envoyé se termine dans new
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    if not old_lines:
        return new
    # Trouver la dernière ligne non-vide de old comme ancre
    last_old = ""
    trim_at = len(old_lines)
    for k in range(len(old_lines) - 1, -1, -1):
        if old_lines[k].strip():
            last_old = old_lines[k].strip()
            trim_at = k + 1
            break
    if not last_old:
        return new
    # Chercher cette ancre dans new (en partant de la fin)
    for i in range(len(new_lines) - 1, -1, -1):
        if new_lines[i].strip() == last_old:
            match_count = 1
            for j in range(1, min(trim_at, i + 1)):
                if old_lines[trim_at - 1 - j].strip() == new_lines[i - j].strip():
                    match_count += 1
                else:
                    break
            if match_count >= min(2, trim_at):
                after = new_lines[i + 1:]
                return "\n".join(after).strip() if after else ""
    return new


async def send_chunks(update: Update, text: str):
    """Envoie un texte, découpé en plusieurs messages si nécessaire."""
    lines = text.splitlines()
    chunks = []
    current = []
    current_len = 0
    for line in lines:
        if current_len + len(line) + 1 > 3900 and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    for chunk in chunks:
        await update.message.reply_text(
            f"<pre>{html.escape(chunk)}</pre>", parse_mode="HTML"
        )


async def auto_read(update: Update):
    """Surveille le terminal et envoie les diffs au fur et à mesure que Claude répond."""
    global _last_response
    await asyncio.sleep(1)
    sent_any = False
    stable_count = 0
    previous_raw = ""
    for _ in range(120):
        output = run(f"tmux capture-pane -t {SESSION_NAME} -p -S -500")
        response = extract_response(output)
        # Envoyer le diff si nouveau contenu détecté
        if response and response != _last_response:
            diff = compute_diff(_last_response, response)
            if diff:
                await send_chunks(update, diff)
                sent_any = True
            _last_response = response
        # Dialogue interactif (permission, confirmation…) → envoyer et sortir
        dialog = extract_dialog(output)
        if dialog:
            await update.message.reply_text(
                f"<pre>{html.escape(dialog)}</pre>", parse_mode="HTML"
            )
            return
        # Claude a fini ? Double-check après 1s pour éviter les faux positifs
        if is_claude_done(output):
            await asyncio.sleep(1)
            output = run(f"tmux capture-pane -t {SESSION_NAME} -p -S -500")
            if not is_claude_done(output):
                continue  # Faux positif, Claude travaille encore
            # Vérifier si un dialogue est apparu pendant le délai
            dialog = extract_dialog(output)
            if dialog:
                final = extract_response(output)
                if final and final != _last_response:
                    diff = compute_diff(_last_response, final)
                    if diff:
                        await send_chunks(update, diff)
                    _last_response = final
                await update.message.reply_text(
                    f"<pre>{html.escape(dialog)}</pre>", parse_mode="HTML"
                )
                return
            final = extract_response(output)
            if final and final != _last_response:
                diff = compute_diff(_last_response, final)
                if diff:
                    await send_chunks(update, diff)
                    sent_any = True
                _last_response = final
            if not sent_any:
                await update.message.reply_text("(aucun changement)")
            return
        # Fallback stabilité : 5× identique sans prompt → sortir
        if output == previous_raw:
            stable_count += 1
            if stable_count >= 5:
                if not sent_any:
                    await update.message.reply_text("(aucun changement)")
                return
        else:
            stable_count = 0
            previous_raw = output
        await asyncio.sleep(1)
    if not sent_any:
        await update.message.reply_text("(timeout)")


@auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot Claude Code prêt.\n\n"
        "/open — Ouvrir une session\n"
        "/close — Fermer la session\n"
        "/y /n — Confirmer / Refuser\n"
        "/esc — Annuler\n"
        "/pick N — Choisir l'option N\n\n"
        "Envoie un message texte pour parler à Claude."
    )


@auth
async def open_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_exists():
        await update.message.reply_text("Session déjà active.")
        return
    run(f"tmux new-session -d -s {SESSION_NAME} -x 200 -y 50")
    run(f"tmux send-keys -t {SESSION_NAME} -l claude")
    run(f"tmux send-keys -t {SESSION_NAME} Enter")
    await update.message.reply_text("Session Claude Code ouverte.")
    await auto_read(update)


@auth
async def close_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not session_exists():
        await update.message.reply_text("Aucune session active.")
        return
    global _last_response
    run(f"tmux kill-session -t {SESSION_NAME}")
    _last_response = ""
    await update.message.reply_text("Session fermée.")


@auth
async def plain_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Les messages sans commande sont envoyés directement à la session Claude."""
    if not session_exists():
        await update.message.reply_text("Aucune session active. /open d'abord.")
        return
    msg = update.message.text
    run(f"tmux send-keys -t {SESSION_NAME} -l {subprocess.list2cmdline([msg])}")
    run(f"tmux send-keys -t {SESSION_NAME} Enter")
    await auto_read(update)


def make_key_handler(key: str):
    """Factory pour créer un handler qui envoie une touche tmux."""
    @auth
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not session_exists():
            await update.message.reply_text("Aucune session active. /open d'abord.")
            return
        run(f"tmux send-keys -t {SESSION_NAME} {key}")
        await auto_read(update)
    return handler


@auth
async def pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sélectionne l'option N dans un menu interactif (N flèches bas + Enter)."""
    if not session_exists():
        await update.message.reply_text("Aucune session active. /open d'abord.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /pick <N>")
        return
    n = int(context.args[0])
    for _ in range(max(0, n - 1)):
        run(f"tmux send-keys -t {SESSION_NAME} Down")
    run(f"tmux send-keys -t {SESSION_NAME} Enter")
    await auto_read(update)


async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("open", "Ouvrir une session"),
        BotCommand("close", "Fermer la session"),
        BotCommand("y", "Confirmer (Yes)"),
        BotCommand("n", "Refuser (No)"),
        BotCommand("esc", "Annuler (Escape)"),
        BotCommand("pick", "Choisir l'option N"),
    ])


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("open", open_session))
    app.add_handler(CommandHandler("close", close_session))
    app.add_handler(CommandHandler("y", make_key_handler("y")))
    app.add_handler(CommandHandler("n", make_key_handler("n")))
    app.add_handler(CommandHandler("esc", make_key_handler("Escape")))
    app.add_handler(CommandHandler("pick", pick))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_message))
    print("Bot démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
