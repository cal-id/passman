#! /usr/bin/env python3
"""Very simple password storing application.

Usage:
    python3 cli.py
    password: <enter password>
    <cmd>
    <response>
"""

import getpass
import utils
import json
from os.path import isfile
from shutil import copyfile
import time


STORED_FILE_NAME = "store.enc"


COMMANDS = {
    "list": "Lists the titles of all saved entries.",
    "help": "Displays a list of commands and attributes",
    "show <Title>": "Shows info about a given title.",
    "set <Title>": "Prompts setting a given title.",
    "undo": "Resets any changes made this log in.",
    "exit": "Quits the program."
}
MAX_COMMAND_LENGTH = max(len(key) for key in COMMANDS)


ATTRIBUTES = {
    "Title": "the (unique) title of this entry",
    "Password": "the saved password",
    "Email": "the associated email address",
    "Notes": "any notes for this entry",
    "Username": "the username for this entry"
}

MAX_ATTRIBUTE_LENGTH = max(len(key) for key in ATTRIBUTES)


originalFileBeforeChange = None


def readToDict(encryption_password):
    """Reads the encrypted file and parses the json into a dict of
    dicts containing attributes about each entry.

    {
        "Gmail": {"Password":"not this", "Email":...},
        "Facebook": {},
        "Youtube": {}, ...
    }

    Stores the dict of passwords in the global stored_passwords."""
    if not isfile(STORED_FILE_NAME):
        passwords = {}  # If there is no file then return empty list
    else:
        raw = utils.decryptFromFile(STORED_FILE_NAME, encryption_password
                                    ).decode()
        passwords = json.loads(raw)
    global stored_passwords
    stored_passwords = passwords


def writeDictToFile():
    """Takes a list of dictionaries as in readToList(), strigifies it with
    JSON and then writes to an encrypted file."""
    backupFile = time.strftime(".backup-%Y%m%d-%H%M%S.enc")
    global originalFileBeforeChange
    if originalFileBeforeChange is None:
        originalFileBeforeChange = backupFile
    if isfile(STORED_FILE_NAME):
        copyfile(STORED_FILE_NAME, backupFile)
    utils.encryptToFile(STORED_FILE_NAME, json.dumps(stored_passwords),
                        encryption_password)


def executeCommand(cmd):
    """Runs the command specified in the input string cmd."""
    directive = cmd.split(" ")[0]
    for key in COMMANDS:
        if key.startswith(directive):
            if directive == "list":
                return display_list()
            if directive == "help":
                return display_help()
            if directive == "show":
                return display_show(cmd.split(" ")[1])
            if directive == "set":
                return display_set(cmd.split(" ")[1])
            if directive == "undo":
                return undo()
            if directive == "exit":
                global running
                running = False
                return
    print("Unrecognised Command, try 'help'.")


def fmtAttribute(attr):
    "Right pads attribute by the largest attribute."
    return ("{:" + str(MAX_ATTRIBUTE_LENGTH) + "}").format(attr)


def fmtCommand(cmd):
    "Right pads command by the largest command."
    return ("{:" + str(MAX_COMMAND_LENGTH) + "}").format(cmd)





def display_list():
    """Given a dict of password dicts, it displays a list of their
    titles"""
    for key in stored_passwords:
        print(key)


def display_help():
    "Shows a list of possible commands"
    for cmd, desc in COMMANDS.items():
        print("{} {}".format(fmtCommand(cmd), desc))


def display_show(title):
    "Shows info about a given title"
    if title in stored_passwords:
        data = stored_passwords[title]
        for attribute in ATTRIBUTES:
            val = ("-" if attribute not in data
                   else "********" if attribute == "Password"
                   else data[attribute])
            print("{} {}".format(fmtAttribute(attribute), val))
    else:
        print("Title not found in stored passwords.")


def display_set(title):
    "Sets data for a given title"
    updated = False
    if title in stored_passwords:
        data = stored_passwords[title]
    else:
        data = {}
        updated = True
    print("Setting data for {}, leave blank for no entry or "
          "old value.".format(title))
    for attribute in ATTRIBUTES:
        if attribute == "Password":
            print("Enter password twice.")
            newPass1 = getpass.getpass()
            if newPass1 == "":
                continue
            newPass2 = getpass.getpass()
            while newPass1 != newPass2:
                print("Passwords don't match try again.")
                newPass1 = getpass.getpass()
                if newPass1 == "":
                    break
                newPass2 = getpass.getpass()
            if newPass1 != "":
                print(" Set password")
        elif attribute != "Title":
            val = "-" if attribute not in data else data[attribute]
            newVal = input("Update {} from {}:".format(attribute, val))
            if newVal != "":
                updated = True
                print(" Set {}: {} > {}".format(fmtAttribute(attribute),
                                                val, newVal))
                data[attribute] = newVal
    if updated:
        print("Saving changed file")
        stored_passwords[title] = data
        writeDictToFile()
    else:
        print("Not updated, not saving.")


def undo():
    if originalFileBeforeChange is None:
        print("Nothing to undo")
    else:
        copyfile(originalFileBeforeChange, STORED_FILE_NAME)
        readToDict(encryption_password)
        print("Reset to before any changes this log in.")


if __name__ == "__main__":
    print(__doc__)
    encryption_password = getpass.getpass()
    readToDict(encryption_password)
    running = True
    while running:
        executeCommand(input(">"))
