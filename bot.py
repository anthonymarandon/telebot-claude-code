import os
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
SESSION_NAME = "claude"


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


@auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot Claude Code prêt.\n\n"
        "/open — Ouvrir une session Claude Code\n"
        "/send <msg> — Envoyer un message à Claude\n"
        "/read — Lire la sortie du terminal\n"
        "/close — Fermer la session\n"
        "/status — État de la session\n"
        "/cmd <commande> — Exécuter une commande shell"
    )


@auth
async def open_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_exists():
        await update.message.reply_text("Session déjà active.")
        return
    run(f"tmux new-session -d -s {SESSION_NAME} -x 200 -y 50")
    run(f"tmux send-keys -t {SESSION_NAME} 'claude' Enter")
    await update.message.reply_text("Session Claude Code ouverte.")


@auth
async def send_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not session_exists():
        await update.message.reply_text("Aucune session active. /open d'abord.")
        return
    msg = " ".join(context.args) if context.args else ""
    if not msg:
        await update.message.reply_text("Usage: /send <message>")
        return
    run(f"tmux send-keys -t {SESSION_NAME} {subprocess.list2cmdline([msg])} Enter")
    await update.message.reply_text(f"Envoyé.")


@auth
async def read_output(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not session_exists():
        await update.message.reply_text("Aucune session active.")
        return
    output = run(f"tmux capture-pane -t {SESSION_NAME} -p -S -50")
    if not output:
        output = "(vide)"
    # Telegram limite les messages à 4096 caractères
    if len(output) > 4000:
        output = output[-4000:]
    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")


@auth
async def close_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not session_exists():
        await update.message.reply_text("Aucune session active.")
        return
    run(f"tmux kill-session -t {SESSION_NAME}")
    await update.message.reply_text("Session fermée.")


@auth
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_exists():
        await update.message.reply_text("Session active.")
    else:
        await update.message.reply_text("Aucune session active.")


@auth
async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = " ".join(context.args) if context.args else ""
    if not command:
        await update.message.reply_text("Usage: /cmd <commande>")
        return
    output = run(command)
    if not output:
        output = "(aucune sortie)"
    if len(output) > 4000:
        output = output[-4000:]
    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")


@auth
async def plain_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Les messages sans commande sont envoyés directement à la session Claude."""
    if not session_exists():
        await update.message.reply_text("Aucune session active. /open d'abord.")
        return
    msg = update.message.text
    run(f"tmux send-keys -t {SESSION_NAME} {subprocess.list2cmdline([msg])} Enter")
    await update.message.reply_text("Envoyé.")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("open", open_session))
    app.add_handler(CommandHandler("send", send_msg))
    app.add_handler(CommandHandler("read", read_output))
    app.add_handler(CommandHandler("close", close_session))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_message))
    print("Bot démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
