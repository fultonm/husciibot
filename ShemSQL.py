"""
    Holds the SQL statements used by HusciiBot. The SQLite version of stored procs.

    Authors: Michael Fulton
"""

INSERT_EVENT = "INSERT INTO events (date, description, created_by) VALUES (?, ?, ?)"
REMOVE_EVENT = "DELETE FROM events WHERE id in \
                    (SELECT event_id FROM selected_events WHERE id=?)"
FIND_EVENT = "SELECT * FROM events WHERE string LIKE %?% LIMIT 5"
UPCOMING_EVENTS = "SELECT * FROM selected_events INNER JOIN events ON \
                    selected_events.event_id = events.id"
# selected_events table is an auxiliary table created after HusciiBot lists the events.
# This makes it easier for a user to selected which event to update or delete.
CREATE_SELECTED_EVENTS = "CREATE TABLE selected_events (\
                            id INTEGER PRIMARY KEY AUTOINCREMENT,\
                            event_id INTEGER NOT NULL)"
# The selected events list need to be ordered from recent to far, with past dates omitted.
INSERT_SELECTED_EVENTS = "INSERT INTO selected_events (event_id)\
                            SELECT id FROM events\
                            WHERE date(\
                                substr(events.date,7,4)||\"-\"||\
                                substr(events.date,1,2)||\"-\"||\
                                substr(events.date,4,2)) >= date('now')\
                            ORDER BY date(\
                                substr(events.date,7,4)||\"-\"||\
                                substr(events.date,1,2)||\"-\"||\
                                substr(events.date,4,2)) ASC LIMIT 5"
DROP_SELECTED_EVENTS = "DROP TABLE selected_events"
COUNT_SELECTED_EVENTS = "SELECT COUNT(*) FROM selected_events"
CHECK_SELECTED_EVENTS_EXISTS = "SELECT name FROM sqlite_master WHERE \
                                    type='table' and name='selected_events'"
# Officer functions
CHECK_OFFICER = "SELECT * FROM officers WHERE id=?"
ADD_OFFICER = "INSERT INTO officers (id) VALUES (?)"
REMOVE_OFFICER = "DELETE FROM officers WHERE id=?"
