"""
    Provides authentication methods for various HusciiBot services.
"""
import sqlite3
import re
import json
import requests

import ShemSQL
import HusciiKeys

CONN = sqlite3.connect('b.db')
C = CONN.cursor()

def handle_command(command, user):
    """
        Parses and processes commands incoming to the authentication module.

        command: The command string provided by the user
        user: The 9 character user ID of the user issuing the command.
    """
    command = replace_quotation(command)
    command_lower = command.lower()
    if 'add' in command_lower:
        officer = extract_user_id(command)
        if officer:
            if insert_officer(officer, user):
                officer_name = get_user_info(officer)['name']
                return 'Added ' + officer_name + ' to officers! They may now modify the\
                        calendar'
            else:
                return officer_action_gate('add', user)
        else:
            return 'Which officer would you like to add?'
    elif 'remove' in command_lower:
        officer = extract_user_id(command)
        if officer:
            if delete_officer(officer, user):
                officer_name = get_user_info(officer)['name']
                return 'Removed ' + officer_name + ' from officers.'
            else:
                return officer_action_gate('remove', user)
        else:
            return 'Which officer would you like to remove?'
    else:
        return 'Valid officer commands are add and remove. (e.x: \"remove officer\
                @JohnGalt\")'

def officer_action_gate(action, user):
    """
        Creates a message containing the action that has been disallowed and the
        user's user ID for debugging purposes.

        action: The string containing which action was attempted.
        user: The nine character slack user id
    """
    return 'Only an officer may ' + action + ' an officer. Your user ID is ' + user

def extract_user_id(command):
    """
        Parses a command string for a 9 character Slack user ID

        command: The command to parse.
    """
    com_split = command.split()
    if len(com_split) > 2:
        user_id = com_split[2]
        user_id = user_id[2:len(user_id) - 1]
        if user_id:
            return user_id
        else:
            return False
    else:
        return False

def get_user_info(user):
    """
        Polls the Slack API for user information using their user ID

        user: The 9 character user ID
    """
    params = {
        'token': HusciiKeys.KEY,
        'user': user
    }
    request = requests.get('https://slack.com/api/users.info', params)
    user_info = json.loads(request.text)
    if user_info and user_info['ok']:
        return user_info['user']
    else:
        return False


def is_officer(user):
    """
        Executes SQL to check whether the given user id is present in the officers table.

        user: The 9 character user id string
    """
    C.execute(ShemSQL.CHECK_OFFICER, (user, ))
    return len(C.fetchall()) > 0


def insert_officer(officer, user):
    """
        Adds another user as an officer. Only an officer may add an officer. If there are
        no officers, a 9 character user ID must be added manually to the table.

        officer: The 9 character Slack user ID to add as an officer.
        user: The 9 character user ID of the user adding a new officer.
    """
    response = False
    if is_officer(user):
        C.execute(ShemSQL.ADD_OFFICER, (officer, ))
        commit()
        response = True
    else:
        response = False
    return response


def delete_officer(officer, user):
    """
        Deletes an officer. Only an officer may delete an officer. If there are
        no officers, a 9 character user ID must be added manually to the table.

        officer: The 9 character Slack user ID to delete from officers.
        user: The 9 character user ID of the user deleting the officer.
    """
    response = False
    if is_officer(user):
        C.execute(ShemSQL.REMOVE_OFFICER, (officer, ))
        commit()
        response = True
    else:
        response = False
    return response


def commit():
    """
        Commits any SQL that has been executed on the DB. All executed SQL is only
        tenative, and nothing happens until commit is finally called.
    """
    CONN.commit()

def replace_quotation(string):
    """
        Helper method replaces any non-standard quotations such as curly quotations with
        standard, straight quotations

        string: The original string to replace quotations on
    """
    quote = '"'
    return string.replace(u'\u201c', quote).replace(u'\u201d', quote).replace('“', quote)\
        .replace('”', quote)
