#!/usr/bin/python3

# This script will set a password based on a file (words.txt) and will select a random word out of that file and set it as password.
# Once set as password, it'll check if the service is either stopped or running, based on that it'll start or restart the service.
# Meanwhile, it'll post a message to the webhook so people in that channel will know a password has been set.

# ======================= Preamble =====================================

# To make optimal use of this program, you have to set it as a task in Windows Schedulded task using a batch file.

# ======================= Imports =====================================

import random

# For interaction with the host OS
from pathlib import Path, PureWindowsPath

import requests
import win32serviceutil

# ======================= Metadata =====================================

AUTHOR = "Bas Imth"
LICENSE = "GPL-3"
SCRIPT_VERSION = 1.0
HEADERTEXT = """pugPassGenerator sets a password for the PUG based on a random line in its input file."""

# ======================= Config ======================================

# Global variables

# Name of the service the game is running on.
SERVICE = ""

# Webhook used to notify the channel.
WEBHOOK = ""

# IT IS NECESSARY TO USE THE FULL PATH WHEN USING WINDOWS TASK SCHEDULER
# Path to the UDKGame.ini for GamePassword.
CONFIG = Path("pug/UDKGame/Config/UDKGame.ini")

# Path to the words.txt for words.
RANDOM = Path("templates/Random/words.txt")

# ======================= Functions =====================================


def version_information():
    print(
        "Author: {} \nLicense: {}\nVersion: {}".format(AUTHOR, LICENSE, SCRIPT_VERSION)
    )


def password_generator():
    with open(RANDOM, "r") as file:
        all_text = file.read()
    words = list(map(str, all_text.split()))

    password = random.choice(words)
    password_setter(password)


def password_setter(password):
    print(password)
    with open(CONFIG, "r") as file:
        load = file.readlines()
    for i, line in enumerate(load):
        if line.startswith("GamePassword"):
            print("GamePassword=" + password)
            load[i] = "GamePassword=" + password + "\n"
    # And write everything back.
    with open(CONFIG, "w") as setter:
        setter.writelines(load)
    service_manager()
    prepare_message(password)


def service_manager():
    running = service_running(SERVICE)
    if not running:
        win32serviceutil.StartService(SERVICE)
        print("Starting")
    else:
        win32serviceutil.RestartService(SERVICE)
        print("Restarting")
    return


def service_running(service):
    return win32serviceutil.QueryServiceStatus(service)


def prepare_message(password):
    data = {"content": "", "username": "Sho's clone"}
    data["embeds"] = [
        {"description": "PUG Password: {}".format(password), "title": "Password set!"}
    ]
    notify_webhook(data)


def notify_webhook(data):
    message = requests.post(WEBHOOK, json=data)
    try:
        message.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(message.status_code))


def main():
    version_information()
    password_generator()

    # ======================= Main =====================================


main()
