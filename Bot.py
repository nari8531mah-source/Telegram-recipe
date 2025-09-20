import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import os

TOKEN = os.getenv("TOKEN")  # توکن از Railway میاد

# دیتابیس
conn = sqlite3.connect("recipes.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS ingredients (name TEXT, cal_per_unit REAL)")
c.execute("CREATE TABLE IF NOT EXISTS recipes (name TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS items (recipe TEXT, ingredient TEXT, amount REAL)")
conn.commit()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من بات رسپی‌ام. از دستورها استفاده کن:\n/add_ingredient\n/add_recipe\n/add_item\n/show\n/search")

async def add_ingredient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name, cal = context.args[0], float(context.args[1])
        c.execute("INSERT INTO ingredients VALUES (?, ?)", (name, cal))
        conn.commit()
        await update.message.reply_text(f"✅ ماده '{name}' با {cal} کالری در واحد اضافه شد.")
    except:
        await update.message.reply_text("❌ فرمت درست: /add_ingredient نام کالری")

async def add_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.args[0]
        c.execute("INSERT INTO recipes VALUES (?)", (name,))
        conn.commit()
        await update.message.reply_text(f"✅ رسپی '{name}' ساخته شد.")
    except:
        await update.message.reply_text("❌ فرمت درست: /add_recipe نام")

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        recipe, ingredient, amount = context.args[0], context.args[1], float(context.args[2])
        c.execute("INSERT INTO items VALUES (?, ?, ?)", (recipe, ingredient, amount))
        conn.commit()
        await update.message.reply_text(f"✅ {amount} واحد از '{ingredient}' به '{recipe}' اضافه شد.")
    except:
        await update.message.reply_text("❌ فرمت درست: /add_item رسپی ماده مقدار")

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        recipe = context.args[0]
        c.execute("SELECT ingredient, amount FROM items WHERE recipe=?", (recipe,))
        items = c.fetchall()
        if not items:
            await update.message.reply_text("❌ چنین رسپی‌ای پیدا نشد.")
            return
        total = 0
        text = f"📖 رسپی {recipe}:\n"
        for ing, amt in items:
            c.execute("SELECT cal_per_unit FROM ingredients WHERE name=?", (ing,))
            cal = c.fetchone()
            if cal:
                kcal = cal[0] * amt
                total += kcal
                text += f"- {ing}: {amt} واحد → {kcal:.2f} کالری\n"
        text += f"\n🔥 مجموع: {total:.2f} کالری"
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("❌ فرمت درست: /show نام_رسپی")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyword = context.args[0]
        c.execute("SELECT name FROM recipes WHERE name LIKE ?", ('%' + keyword + '%',))
        results = c.fetchall()
        if results:
            text = "🔎 رسپی‌های یافت‌شده:\n" + "\n".join([r[0] for r in results])
        else:
            text = "❌ چیزی پیدا نشد."
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("❌ فرمت درست: /search کلمه")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_ingredient", add_ingredient))
    app.add_handler(CommandHandler("add_recipe", add_recipe))
    app.add_handler(CommandHandler("add_item", add_item))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler("search", search))
    app.run_polling()

if __name__ == "__main__":
    main()
