from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, PicklePersistence
from telegram import ParseMode

import fitbot.credentials as cred


def start(update, context):
    query = update.callback_query
    if "workouts" not in context.user_data:
        context.user_data["workouts"] = {}
    if "callback" not in context.user_data:
        context.user_data["callback"] = None
    if "args" not in context.user_data:
        context.user_data["args"] = {}
    menu = [
        [InlineKeyboardButton("Workouts", callback_data="show_workouts")]
    ]
    create_callback_menu(update, "Bitte wähle eine Aktion aus:", menu)


def show_workouts(update, context):
    text = "Wähle ein Workout aus:"
    menu = [[InlineKeyboardButton(n, callback_data=f"show_workout {n}")] for n in context.user_data["workouts"]]
    menu.append([InlineKeyboardButton("+ Workout hinzufügen", callback_data="add_workout")])
    menu.append([InlineKeyboardButton("- Zurück", callback_data="cancel")])
    create_callback_menu(update, text, menu)


def show_workout(update, context, name):
    text = f"*Workout {name}*:"
    for ex in context.user_data["workouts"][name]["exercises"]:
        text += f"\n- {ex['name']}"
    menu = [
        [InlineKeyboardButton("Übungen bearbeiten", callback_data=f"show_exercises {name}")],
        [InlineKeyboardButton("- Zurück", callback_data="show_workouts")]
    ]
    create_callback_menu(update, text, menu)


def get_workout_name(update, context):  # TODO: currently no names with whitespaces possible
    query = update.callback_query
    query.edit_message_text("Füge ein neues Workout hinzu.\n"
                            "Gib deinem Workout einen Namen:")
    context.user_data["callback"] = create_workout


def create_workout(update, context, params):
    name = params["msg"]
    if name in context.user_data["workouts"]:
        update.message.reply_text("Dieser Name existiert bereits!")
        update.message.reply_text("Gib deinem Workout einen anderen Namen:")
        clear_callback(context)
        context.user_data["callback"] = create_workout
    else:
        context.user_data["workouts"][name] = {"name": name, "exercises": []}
        show_exercises(update, context, name)


def show_exercises(update, context, name):
    query = update.callback_query
    text = f"Wähle eine Übung von {name} zum Bearbeiten aus:"
    menu = [[InlineKeyboardButton(ex["name"], callback_data=f"show_exercise {name} {i}")]
            for i, ex in enumerate(context.user_data["workouts"][name]["exercises"])]
    menu.append([InlineKeyboardButton("+ Übung hinzufügen", callback_data=f"show_exercise {name} -1")])
    menu.append([InlineKeyboardButton("- Zurück", callback_data=f"show_workout {name}")])
    create_callback_menu(update, text, menu)


def add_exercise(update, context, params):
    workout_name = params["workout_name"]
    exercise_name = params["msg"]
    clear_callback(context)
    context.user_data["workouts"][workout_name]["exercises"].append({"name": exercise_name, "sets": "3", "reps": "12"})
    show_exercises(update, context, workout_name)


def show_exercise(update, context, name, idx):
    query = update.callback_query
    if idx == -1:
        query.edit_message_text(text="Gib der Übung einen Namen:")
        context.user_data["callback"] = add_exercise
        context.user_data["args"] = {"workout_name": name}
    else:
        ex = context.user_data["workouts"][name]["exercises"][idx]
        text = f"Was möchtest du bearbeiten?"
        menu = [
            [InlineKeyboardButton(f"Name: {ex['name']}", callback_data=f"edit_exercise {name} {idx} name")],
            [InlineKeyboardButton(f"Sätze: {ex['sets']}", callback_data=f"edit_exercise {name} {idx} sets")],
            [InlineKeyboardButton(f"Wiederholungen: {ex['reps']}", callback_data=f"edit_exercise {name} {idx} reps")],
            [InlineKeyboardButton("- Zurück", callback_data=f"show_exercises {name}")]
        ]
        create_callback_menu(update, text, menu)


def edit_exercise(update, context, name, idx, param):
    param_text = ""
    if param == "name":
        param_text = "Gib einen neuen Namen für die Übung ein:"
    elif param == "sets":
        param_text = "Gib eine Anzahl an Sätzen für die Übung ein:"
    elif param == "reps":
        param_text = "Gib eine Anzahl an Wiederholungen für die Übung ein:"
    query = update.callback_query
    query.edit_message_text(param_text)
    context.user_data["callback"] = edit_exercise_property
    context.user_data["args"] = {"workout_name": name, "exercise_idx": idx, "property": param}


def edit_exercise_property(update, context, params):
    workout_name = params["workout_name"]
    exercise_idx = params["exercise_idx"]
    property_key = params["property"]
    property_val = params["msg"]
    context.user_data["workouts"][workout_name]["exercises"][exercise_idx][property_key] = property_val
    clear_callback(context)
    show_exercise(update, context, workout_name, exercise_idx)


def create_callback_menu(update, text, menu):
    if update.message is not None:
        update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(menu), parse_mode=ParseMode.MARKDOWN)
    else:
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(menu),
                                                parse_mode=ParseMode.MARKDOWN)


def callback_query_handler(update, context):
    input_list = update.callback_query.data.split(" ")
    update.callback_query.answer()
    if input_list[0] == 'show_workouts':
        show_workouts(update, context)
    elif input_list[0] == 'show_workout':
        show_workout(update, context, input_list[1])
    elif input_list[0] == 'add_workout':
        get_workout_name(update, context)
    elif input_list[0] == 'show_exercises':
        show_exercises(update, context, input_list[1])
    elif input_list[0] == 'show_exercise':
        show_exercise(update, context, input_list[1], int(input_list[2]))
    elif input_list[0] == 'edit_exercise':
        edit_exercise(update, context, input_list[1], int(input_list[2]), input_list[3])
    elif input_list[0] == 'cancel':
        start(update, context)
    else:
        print(input_list)


def get_string(update, context):
    if "callback" not in context.user_data or not context.user_data["callback"]:
        print(update.message.text)
        return
    context.user_data["args"]["msg"] = update.message.text
    context.user_data["callback"](update, context, context.user_data["args"])


def clear_callback(context):
    context.user_data["callback"] = None
    context.user_data["args"] = {}


def main():
    persistence = PicklePersistence("./db")
    updater = Updater(cred.bot_token, use_context=True, persistence=persistence)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    dp.add_handler(MessageHandler(Filters.text, get_string))

    updater.start_polling()
    updater.idle()
