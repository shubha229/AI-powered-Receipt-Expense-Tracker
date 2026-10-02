from datetime import datetime

from database import (
    expenses_collection,
    settings_collection
)


# ============================================================
# ADD EXPENSE
# ============================================================

def add_expense(user, expense):

    expense["user"] = user
    expense["created_at"] = datetime.now()

    expenses_collection.insert_one(expense)


# ============================================================
# GET EXPENSES
# ============================================================

def get_expenses(user):

    expenses = list(
        expenses_collection.find(
            {"user": user}
        ).sort(
            "created_at",
            -1
        )
    )

    return expenses


# ============================================================
# DELETE EXPENSE
# ============================================================

def delete_expense(expense_id):

    expenses_collection.delete_one(
        {"_id": expense_id}
    )


# ============================================================
# GET MONTHLY BUDGET
# ============================================================

def get_budget(user):

    data = settings_collection.find_one(
        {"user": user}
    )

    if data:

        return data.get(
            "monthly_budget",
            0
        )

    return 0


# ============================================================
# SAVE MONTHLY BUDGET
# ============================================================

def save_budget(user, amount):

    settings_collection.update_one(
        {"user": user},
        {
            "$set": {
                "user": user,
                "monthly_budget": amount
            }
        },
        upsert=True
    )