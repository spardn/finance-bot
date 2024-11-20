from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime

# Initialize user data
user_data = {}

# Command to start the bot and set budget
def start(update, context):
    update.message.reply_text("Welcome! Please set your monthly budget using /set_budget <amount>.")

# Command to set the monthly budget
def set_budget(update, context):
    try:
        monthly_budget = int(context.args[0])
        user_data[update.message.chat_id] = {
            'monthly_budget': monthly_budget,
            'fixed_expenses': 0,
            'daily_budget': 0,
            'expenses': [],
        }
        update.message.reply_text("Monthly budget set! Now set your fixed expenses using /set_expenses <amount>.")
    except (IndexError, ValueError):
        update.message.reply_text("Please provide a valid amount. Example: /set_budget 30000")

# Command to set fixed expenses
def set_expenses(update, context):
    try:
        fixed_expenses = int(context.args[0])
        user = user_data.get(update.message.chat_id)
        if user:
            daily_budget = (user['monthly_budget'] - fixed_expenses) // 30
            user.update({'fixed_expenses': fixed_expenses, 'daily_budget': daily_budget})
            update.message.reply_text(f"Fixed expenses set! Your daily budget is: {daily_budget} rs.")
        else:
            update.message.reply_text("Please set your monthly budget first using /set_budget.")
    except (IndexError, ValueError):
        update.message.reply_text("Please provide a valid amount. Example: /set_expenses 5000")

# Logging expenses
def log_expense(update, context):
    user = user_data.get(update.message.chat_id)
    if user:
        try:
            message = update.message.text
            product, amount = message.split('=')
            amount = int(amount.strip())
            user['daily_budget'] -= amount
            user['expenses'].append((product.strip(), amount))
            update.message.reply_text(
                f"Expense logged! Remaining balance: {user['daily_budget']} rs."
            )
        except ValueError:
            update.message.reply_text("Invalid format. Please use: Product=Amount (e.g., Egg roll=70).")
    else:
        update.message.reply_text("Please set your monthly budget first using /set_budget.")

# Daily summary
def summary(update, context):
    user = user_data.get(update.message.chat_id)
    if user:
        expenses = "\n".join([f"{i+1}. {item[0]}: {item[1]}" for i, item in enumerate(user['expenses'])])
        update.message.reply_text(
            f"Daily Budget: {user['monthly_budget'] // 30}\nRemaining Balance: {user['daily_budget']}\nExpenses:\n{expenses}"
        )
    else:
        update.message.reply_text("Please set your monthly budget first using /set_budget.")

# Schedule daily report at 11 PM IST
def daily_report(context):
    for chat_id, user in user_data.items():
        expenses = "\n".join([f"{i+1}. {item[0]}: {item[1]}" for i, item in enumerate(user['expenses'])])
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Daily Report:\nDaily Budget: {user['monthly_budget'] // 30}\nRemaining Balance: {user['daily_budget']}\nExpenses:\n{expenses}"
        )
        # Reset for the next day
        user['daily_budget'] = user['monthly_budget'] // 30
        user['expenses'] = []

# Main function
def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("set_budget", set_budget))
    dp.add_handler(CommandHandler("set_expenses", set_expenses))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, log_expense))
    dp.add_handler(CommandHandler("summary", summary))

    # Schedule daily report
    job_queue = updater.job_queue
    job_queue.run_daily(daily_report, time=datetime.time(23, 0))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()