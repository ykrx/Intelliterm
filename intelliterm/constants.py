import os

import platformdirs

import intelliterm


CODE_THEME = "lightbulb"     # (Pygments theme)

APP_AUTHOR = "Yulian Kraynyak"
USER_DATA_DIR = platformdirs.user_data_dir(intelliterm.__name__, APP_AUTHOR)
DOCUMENTS_DIR = platformdirs.user_documents_dir()
SAVED_CHATS_DIR = os.path.join(DOCUMENTS_DIR, intelliterm.__name__, "chats")
LOGS_DIR = os.path.join(DOCUMENTS_DIR, intelliterm.__name__, "logs")
