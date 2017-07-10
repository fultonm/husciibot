# encoding=utf8
"""
Provides event management for Slack. Quickly add or check out upcoming events!

Authors: Michael Fulton
"""
import sqlite3
import datefinder

import HusciiAuth
# Contains SQL command constants
import ShemSQL

# Connect to SQLite DB and create the cursor.
CONN = sqlite3.connect('b.db')
C = CONN.cursor()


def handle_command(command, user):
    """
        Receives commands which have been determined by HusciiBot to be event related.
        Shem then validates the commands, and provides helpful messages if the commands
        cannot be understood.

        command: The command string given by the user.abs
        user: The 9 character user ID of the user issuing this command.
    """
    # Set response to general error in case it falls through conditionals.
    response = 'I cannot understand what you want to do with the event: ' + \
        command + '\nValid commands are add, list and remove.'
    # Some Slack desktop native clients use curly quotes.
    command = replace_quotation(command)
    command_lower = command.lower()
    if 'add' in command_lower:
        response = add_event(command, user)
    elif 'list' in command_lower:
        return list_events()
    elif 'remove' or 'delete' in command_lower:
        response = remove_event(command, user)
    return response


def remove_event(command, user):
    """
        Removes the event, specified in the command by its position in the selected_events
        SQL table. That table is built from the results of the list_events method here,
        and creates a relationship between the values the user selects for removal (1-5)
        and the event's actual id in the 'events' SQL table.

        command: The user's input from Slack
        user: The 9 character user ID
    """
    response = ''
    if not HusciiAuth.is_officer(user):
        response = HusciiAuth.officer_action_gate('remove club events', user)
    elif not has_selected_event():
        response = 'List the events with \'event list\' first, then remove like \'remove\
                    event 2\''
    elif has_integer(command):
        index = extract_first_integer(command)
        response = remove_selected_event(index, user)
    else:
        response = 'Use the integer numbers shown when listing events to select \
                    which event to remove'
    return response


def list_events():
    """
        Lists events which have yet to occur, ordered by their dates in ascending order.
        Also creates an auxiliary table with index 1-5, so the user can select from these
        to edit or remove the event.
    """
    events_json = find_upcoming_events()
    response = ''
    if events_json:
        for event in events_json:
            selection_id = str(event[0])
            date = event[2]
            description = event[3]
            response += selection_id + ') ' + date + ': ' + description + '\n'
    else:
        response = 'No upcoming events found. Maybe we should plan one?'
    return response


def add_event(command, user):
    """
        Parses the user's command and determines whether all the information necessary
        to create an event is present. If so, this information is inserted into the SQL
        database, otherwise a validation message is returned.

        command: The user's input from Slack
        user: The 9 character user ID
    """
    date = None
    event_desc = None
    if has_date(command):
        date = extract_date(command)
    else:
        return 'I don\'t know what date that is.'
    if not HusciiAuth.is_officer(user):
        return HusciiAuth.officer_action_gate('add or modify club events', user)
    elif has_quoted_str(command):
        event_desc = extract_quoted_str(command)
    else:
        return 'I can\'t understand the event. Make sure it is within quotation marks \
                "like this".'
    event = {
        'description': event_desc,
        'user': user,
        'date': stringify_date(date)
    }
    insert_event(event)
    return event_added_response(event_desc, date)


def event_added_response(event_desc, date):
    """
        Creates and returns a response informing the user their event has been added.abs

        event_desc: The description of the event (i.e. the text between the quotes
                    supplied by the user)
        date: The string representation of the event's date.
    """
    ellipsis = '...' if len(event_desc) > 12 else ''
    short_event_desc = event_desc[0:min(12, len(event_desc))] + ellipsis
    return 'Successfully added ' + short_event_desc + ' on ' + stringify_date(date) + '.'


def replace_quotation(string):
    """
        Helper method replaces any non-standard quotations such as curly quotations with
        standard, straight quotations

        string: The original string to replace quotations on
    """
    quote = '"'
    return string.replace(u'\u201c', quote).replace(u'\u201d', quote).replace('“', quote)\
        .replace('”', quote)


def has_quoted_str(string):
    """
        Returns whether the given string has any value inbetween two quotation marks.

        string: The string to test for the above condition.
    """
    split_str = string.split('"')
    return len(split_str) > 2


def extract_quoted_str(string):
    """
        Returns the value inbetween two quotation marks.

        string: The string to parse.
    """
    split_str = string.split('"')
    return split_str[1]


def has_integer(string):
    """
        Returns whether the given string has an integer

        string: The string to test
    """
    split_str = string.split()
    integers = []
    for seg in split_str:
        if seg.isdigit():
            integers.append(int(seg))
    return len(integers) > 0


def extract_first_integer(string):
    """
        Returns the first integer found in the given string

        string: The string to parse
    """
    split_str = string.split()
    for seg in split_str:
        if seg.isdigit():
            return int(seg)


def has_date(string):
    """
        Returns whether the given string contains a parsable date or represents some date.

        string: The string to test for the above condition
    """
    matches = list(datefinder.find_dates(string))
    return len(matches) > 0


def extract_date(string):
    """
        Returns a date found in the given string.

        string: The string to test.
    """
    matches = list(datefinder.find_dates(string))
    match = ''
    if matches:
        match = matches[0]
    return match


def stringify_date(date):
    """
        Formats a date object into a string. Ex. 1/1/2007

        date: The date to convert to a string.
    """
    return date.strftime('%m/%d/%Y')


# parameter 'user' will eventually be used for authentication. Keeping for now.
# pylint: disable=unused-argument


def remove_selected_event(index, user):
    """
        Executes the SQL responsible for removing an event from the DB.

        index: The index on the selected_events table which cooresponds to an event ID.
               Note: This is not the ID of the event as it is found in the 'events' SQL
               table
        user: The 9 character Slack user ID
    """
    response = ''
    count = C.execute(ShemSQL.COUNT_SELECTED_EVENTS).fetchone()[0]
    if 1 <= index <= count:
        C.execute(ShemSQL.REMOVE_EVENT, str(index))
        C.execute(ShemSQL.DROP_SELECTED_EVENTS)
        commit()
        response = 'Successfully removed event.'
    else:
        response = 'Index not valid'
    return response


def has_selected_event():
    """
        Executes the SQL responsible for checking whether the selected_events table
        exists. Returns true if exists, false if not.
    """
    C.execute(ShemSQL.CHECK_SELECTED_EVENTS_EXISTS)
    return len(C.fetchall()) > 0


def find_upcoming_events():
    """
        Executes the SQL responsible for listing events. Creates an auxiliary
        selected_events table used to create friendly indexing the user can use to select
        a specific event. The INSERT_SELECTED_EVENTS creates a mapping between this
        friendly index and the event's actual ID. Returns the top 5 most imminent events
        which have not already occurred.
    """
    if C.execute(ShemSQL.CHECK_SELECTED_EVENTS_EXISTS).fetchone():
        C.execute(ShemSQL.DROP_SELECTED_EVENTS)
        commit()
    C.execute(ShemSQL.CREATE_SELECTED_EVENTS)
    commit()
    C.execute(ShemSQL.INSERT_SELECTED_EVENTS)
    commit()
    C.execute(ShemSQL.UPCOMING_EVENTS)
    return C.fetchall()


def insert_event(event):
    """
        Executes the SQL responsible for inserting a new event to the events table.

        event: The event object containing date, description, and user ID
    """
    event_info = (event['date'], event['description'], event['user'])
    C.execute(ShemSQL.INSERT_EVENT, event_info)
    commit()


def find_event(string):
    """
        Executes SQL which searching for an event which contains the given string in the
        event's description. Returns a (possibly empty) JSON array with the matches.

        string: The string to match against all events' description.
    """
    C.execute(ShemSQL.FIND_EVENT, string)
    return C.fetchall()


def commit():
    """
        Commits any SQL that has been executed on the DB. All executed SQL is only
        tenative, and nothing happens until commit is finally called.
    """
    CONN.commit()
