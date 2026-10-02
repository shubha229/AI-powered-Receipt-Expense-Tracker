import streamlit as st
from pymongo import MongoClient


# ============================================================
# MONGODB
# ============================================================

MONGO_URI = st.secrets["MONGO_URI"]

client = MongoClient(MONGO_URI)

db = client["smartspend"]

expenses_collection = db["expenses"]

users_collection = db["users"]

settings_collection = db["settings"]