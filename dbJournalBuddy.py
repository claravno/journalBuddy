import datetime
from dbTools import *


class category:

    def create(person_id, name, parent_id=None):
        """ Insert new category into the category table """

        sql = """
        INSERT INTO category(name, person_id, parent_id)
        VALUES(%s, %s, %s)
        RETURNING id
        """

        id = connect(sql, (name, person_id, parent_id), True)
        id = id[0][0]
        print('category id:', id)

        return id

    def update_name(id, name):
        """Update the category name in the category table"""

        sql = """
        UPDATE category
        SET name = %s
        WHERE id = %s 
        """

        connect(sql, (name, id,), False)

    def delete(id):

        sql = """
        DELETE FROM category
        WHERE id = %s 
        """

        connect(sql, (id,), False)


    def return_all(chat_id):
        """Return all categories"""

        print(chat_id)

        sql = """
        SELECT name, id, parent_id
        FROM category
        WHERE person_id = %s
        """

        return connect(sql, (chat_id,), True)[0]


# ------------------------------------------------------------

class goal:

    def create(activity_id, date, measure, measure_type):
        """Create a weekly goal"""

        sql = """
        INSERT INTO habit_week_goal(activity_id, week, measure, measure_type)
        VALUES(%s, %s, %s, %s)
        """

        connect(sql, (activity_id, date, measure, measure_type), False)


    def return_all(person_id, date):
        """Get all logged activities from specific day"""

        sql = """
        SELECT hwg.activity_id,
               a.name,
               c.id as category_id,
               c.name,
               hwg.measure,
               hwg.measure_type,
               sum( coalesce(al.quantity,0) + coalesce(al.duration,0) ) as msr,
               count(*) as fqy
        FROM habit_week_goal as hwg
        LEFT JOIN activity_log as al ON hwg.activity_id = al.activity_id
        JOIN activity a on a.id = hwg.activity_id
        LEFT JOIN category as c ON c.id = a.category_id
        WHERE al.status = 2
        AND hwg.week = date_trunc('week', %s::DATE)::DATE
        AND al.date1 BETWEEN  date_trunc('week', %s::DATE)::DATE AND date_trunc('week', %s::DATE)::DATE +7
        AND a.person_id = %s
        group by al.activity_id,
                 a.name,
                 hwg.activity_id,
                 c.id,
                 c.name,
                 hwg.measure,
                 hwg.measure_type
        """

        return connect(sql, (date, date, date, person_id), True)[0]

# ------------------------------------------------------------

class notes:

    def create(date1, notes, person_id):
        """ Insert new note into the daily_notes table """

        sql = """
                INSERT INTO daily_notes(date1, notes, person_id)
                VALUES(%s, %s, %s)
                RETURNING id
                """

        id = connect(sql, (date1, notes, person_id), True)
        id = id[0][0]
        print('daily note id:', id)

        return id


# ------------------------------------------------------------

class emotion:

    def create(name, strength):
        """ Insert new emotion into the emotions table """

        sql = """
        INSERT INTO emotions(name, strength)
        VALUES(%s, %s)
        RETURNING id
        """

        id = connect(sql, (name, strength), True)
        id = id[0][0]
        print('emotion id:', id)

        return id

    def delete(id):
        """ Delete an emotion from the emotions table """

        sql = """
        DELETE FROM emotions 
        WHERE id = %s 
        RETURNING name
        """

        name = connect(sql, (id,), True)
        print(name, " deleted from the database")

    def locate(name, strength):
        """ Locate  a person from the person table """

        sql = """
                SELECT id FROM emotions 
                WHERE name = %s AND strength = %s
                """

        result = connect(sql, (name, strength,), True)
        result = result[0][0]
        print('id', result, "returned from the database")

        return id

    def register_activity_log(emotion_id, activity_id):
        """Register emotion in emotion_activity_log"""

        sql = """
        INSERT INTO emotion_activity_log(emotion_id, activity_log_id)
        VALUES(%s, %s)
        """

        connect(sql, (emotion_id, activity_id), False)
        print('emotion registered')

    def register_daily_notes(emotion_id, daily_notes_id):
        """Register emotion in emotion_activity_log"""

        sql = """
        INSERT INTO emotion_daily_notes(emotion_id, daily_notes_id)
        VALUES(%s, %s)
        """

        connect(sql, (emotion_id, daily_notes_id), False)
        print('emotion registered')


# ------------------------------------------------------------

class person:

    @staticmethod
    def create(id, name):
        """ Insert a new person into the person table """

        sql = """
        INSERT INTO person(id, name)
        VALUES(%s, %s)
        """

        connect(sql, (id, name,), False)

    @staticmethod
    def delete(person_id):
        """ Delete a person from the person table """
        sql = """
        DELETE FROM person 
        WHERE id = %s 
        RETURNING name
        """

        name = connect(sql, (person_id,), True)
        print(name, " deleted from the database")

    def locate(id):
        """ Locate  a person from the person table """

        sql = """
        SELECT id FROM person 
        WHERE id = %s 
        """

        try:
            id = connect(sql, (id,), True)
            id = id[0][0]
            print(id, "returned from the database")
            return True
            print()
        except:
            return False


# ------------------------------------------------------------

class activity:

    def create(sql, fields):
        """ Insert a new activity into the activity table """

        id = connect(sql, fields, True)
        print(id)
        return id[0][0]


    def cancel(id):
        """ Delete an activity from the activity table """

        sql = """
        UPDATE activity_log
        SET status = 5
        WHERE activity_id = %s
        and status = 1
        """

        connect(sql, (id,), False)


    def update_name(activity_id, name):
        """Update the category name in the category table"""

        sql = """
        UPDATE activity
        SET name = %s
        WHERE id = %s 
        """

        connect(sql, (name, activity_id,), False)


    def locate_by_name(name):
        """ Find a person's id from the activity table """

        sql = """
        SELECT id 
        FROM activity 
        WHERE name = %s 
        """

        try:
            id = connect(sql, (name,), True)
            id = id[0][0]
            print(id, "returned from the database")
            return id
        except:
            return False


    def locate_by_id(id):
        """ Find a person's id from the activity table """

        sql = """
        SELECT name 
        FROM activity 
        WHERE id = %s 
        """

        try:
            return connect(sql, (id,), True)[0]
        except:
            return False


    def get_person_id(id):
        """ get a person_id from the activity table """

        sql = """
        SELECT person_id 
        FROM activity 
        WHERE id = %s 
        """

        person_id = connect(sql, (id,), True)
        person_id = person_id[0][0]

        return person_id


    def schedule(activity_id, status, date, date_precision):
        """ add an activity to the activity_log table """

        date = task.correct_date(date, date_precision)

        sql = """
        INSERT INTO activity_log (activity_id, status, date1, date_precision)
        VALUES (%s, %s, %s, %s)
        """

        connect(sql, (activity_id, status, date, date_precision), False)
        print("activity scheduled for ", date)


    def complete(id):
        """Update status in activity_log to Complete"""

        print('complete:', id)

        sql = """
        UPDATE activity_log 
        SET  status = 2
        WHERE activity_id = %s
        AND status = 1 
        """

        connect(sql, (id,), False)
        print("Activity completed")


    def complete_with_emotion(activity_id, emotion_id):
        """Update status in activity_log to Complete"""

        print('complete:', activity_id)

        sql = """
        UPDATE activity_log 
        SET status = 2, emotion_id = %s
        WHERE activity_id = %s
        AND status = 1
        """

        connect(sql, (emotion_id, activity_id,), False)
        print("Activity completed")


    def complete_now_with_emotion(activity_id, emotion_id):
        """Update status in activity_log to Complete"""

        sql = """
        INSERT INTO activity_log VALUES
        SET status = 2, emotion_id = %s
        WHERE activity_id = %s
        AND status = 1
        """

        connect(sql, (emotion_id, activity_id,), False)
        print("Activity completed")


    def remove_completion(activity_id, date):
        """Update status in activity_log to Pending"""

        sql = """
        UPDATE activity_log 
        SET  status = 1
        WHERE activity_id = %s
        AND date1 = %s 
        """

        connect(sql, (activity_id, date,), False)
        print("Completion removed")


    def reschedule(date, date_precision, activity_id):
        """Changes activity date/date precision"""

        sql = """
        UPDATE activity_log 
        SET date1 = %s, date_precision = %s
        WHERE activity_id = %s 
        """

        connect(sql, (date, date_precision, activity_id), False)


    def edit_category(id, category_id):
        """Changes activity date/date precision"""

        print('helo helo', id, category_id)
        sql = """
        UPDATE activity
        SET  category_id = %s
        WHERE id = %s 
        """

        connect(sql, (category_id, id), False)


    def add_notes(id, notes, log):
        """Add notes to activity/activity_log"""

        if log == True:
            sql = """
            UPDATE activity_log
            SET  notes = %s
            WHERE id = %s 
            """
        else:
            sql = """
            UPDATE activity 
            SET  notes = %s
            WHERE id = %s 
            """

        fields = (notes, id)

        connect(sql, fields, False)
        print("Notes added")


    def return_all(sql, fields):
        """Mother of returns"""

        return connect(sql, fields, True)


    def get_log(id, date):
        """Get all logged activities from specific day"""

        sql = """
        SELECT a.name, al.activity_id, c.name, a.type, al.duration, al.quantity, al.start_time, al.end_time
        FROM activity_log as al
        JOIN activity as a ON a.id = al.activity_id
        LEFT JOIN category as c ON c.id = a.category_id
        WHERE al.date1 = %s
        AND a.person_id = %s
        AND al.status = 2
        ORDER BY a.type
        """

        return connect(sql, (date, id), True)[0]


class task(activity):

    def create(person_id, name):
        """Create new task"""

        sql = '''
        INSERT INTO activity(person_id, type, name)
        VALUES(%s, %s, %s) 
        RETURNING id;
        '''

        return activity.create(sql, (person_id, 'T', name))

    def get_sheet(id, date, date_precision):
        """Parent of all sheets"""

        date = task.correct_date(date, date_precision)

        sql = """
        SELECT a.name, al.activity_id, c.name
        FROM activity_log as al
        JOIN activity as a ON a.id = al.activity_id
        LEFT JOIN category as c ON c.id = a.category_id
        WHERE al.date1 = %s
        AND al.date_precision = %s
        AND a.person_id = %s
        AND al.status = 1
        ORDER BY a.category_id
        """

        return connect(sql, (date, date_precision, id), True)[0]

    def get_daily(id, date):
        """Get daily task sheet"""
        return task.get_sheet(id, date, 'D')

    def get_weekly(id, date):
        """Get weekly task sheet"""
        return task.get_sheet(id, date, 'W')

    def get_monthly(id, date):
        """Get monthly task sheet"""
        return task.get_sheet(id, date, 'M')

    def get_pool(person_id, date):
        """Return task pool"""

        sql = """
        SELECT a.name, al.activity_id, c.name
        FROM activity_log as al
        JOIN activity as a ON a.id = al.activity_id
        LEFT JOIN category as c ON c.id = a.category_id
        WHERE a.person_id = %s
        AND  al.date_precision = %s
        AND al.status = 1
        ORDER BY a.category_id
        """

        return connect(sql, (person_id, 'T'), True)[0]

    def correct_date(date, date_precision):

        if date_precision == 'W':
            #set date to start of chosen week
            date = date - datetime.timedelta(days=date.weekday())

        elif date_precision == 'M':
            #set date to start of chosen month
            date = date.replace(day=1)

        return date

    def return_all(id, date, date_precision):
        """Return all tasks with date and date precision """

        sql = """
        SELECT al.activity_id
        FROM activity_log as al
        JOIN activity as a ON a.id = al.activity_id
        WHERE a.person_id = %s 
        AND al.date1 = %s
        AND al.date_precision = %s
        ORDER BY a.category_id
        """

        return activity.return_all(sql, (id, date, date_precision))[0]

    def pass_over(activity_id, date, date_precision):

        sql = """
        UPDATE activity_log 
        SET status = 6
        WHERE activity_id = %s
        AND status = 1
        """

        connect(sql, (activity_id), False)

        sql = """
        INSERT INTO activity_log(activity_id, date1, date_precision, status) 
        VALUES (%s, %s, %s, 1)
        """

        connect(sql, (activity_id, date, date_precision), False)


class habit(activity):

    def create(person_id, name):
        """Create new habit"""

        sql = '''
        INSERT INTO activity(person_id, type, name)
        VALUES(%s, %s, %s) 
        RETURNING id;
        '''

        activity.create(sql, (person_id, 'H', name))

    def deactivate(activity_id):
        """Remove habit from the habit page"""

        sql = '''
        UPDATE activity 
        SET active = FALSE 
        WHERE id = %s
        '''

        connect(sql, (activity_id,), False)

    def return_all(id):
        """Return all habits"""

        sql = """
        SELECT a.name, a.id, a.category_id, c.name, a.measure_type
        FROM activity as a 
        LEFT JOIN category as c ON a.category_id = c.id
        WHERE a.person_id = %s 
        AND a.type = %s
        AND  a.active = TRUE 
        ORDER BY a.category_id
        """

        return activity.return_all(sql, (id, 'H'))[0]

    def complete(activity_id, date, measure, measure_type, emotion_id):
        """Update status in activity_log to Complete"""

        if measure_type == 'D':
            sql = """
            INSERT INTO activity_log(activity_id, date1, status, duration, emotion_id)
            VALUES(%s, %s, 2, %s, %s) 
            """
        else:
            sql = """
            INSERT INTO activity_log(activity_id, date1, status, quantity, emotion_id)
            VALUES(%s, %s, 2, %s, %s) 
            """

        connect(sql, (activity_id, date, measure, emotion_id), False)

    def remove_completion(activity_id, date):
        """Delete habit completion instance from activity_log"""

        sql = """
        DELETE FROM activity_log
        WHERE activity_id = %s
        AND date1 = %s
        """

        connect(sql, (activity_id, date,), False)

    def change_measure_type(activity_id, measure_type):
        """change activity measure type"""

        sql = """
        UPDATE activity
        SET measure_type = %s
        WHERE id = %s 
        """

        connect(sql, (measure_type, activity_id,), False)


class event(activity):

    def create(person_id, name):
        """Create a new event"""

        sql = '''
        INSERT INTO activity(person_id, type, name)
        VALUES(%s, %s, %s) 
        RETURNING id;
        '''

        id = activity.create(sql, (person_id, 'E', name,))
        print("New event id:", id)
        return id

    def return_all(person_id, status):
        """Return all habits"""

        # TO RECEIVE STATUS FOR FORMATTING
        # USE [LEFT JOIN activity as a ON a.id = al.activity_id]
        sql = """
        SELECT a.name, a.id, al.date1, al.start_time, al.end_time, a.category_id, c.name
        FROM activity as a 
        LEFT JOIN category as c ON a.category_id = c.id
        LEFT JOIN activity_log as al ON al.activity_id = a.id
        WHERE a.person_id = %s 
        AND a.type = 'E'
        AND al.status = %s
        ORDER BY al.date1
        """

        return activity.return_all(sql, (person_id, status,))[0]

    def schedule(activity_id, date, start_time, end_time, status):
        """ add an activity to the activity_log table """

        date = task.correct_date(date, start_time)

        sql = """
        INSERT INTO activity_log (activity_id, date1, start_time, end_time, status)
        VALUES (%s, %s, %s, %s, %s)
        """

        connect(sql, (activity_id, date, start_time, end_time, status), False)

    def cancel(activity_id):
        """Remove habit from the habit page"""

        sql = '''
        UPDATE activity_log 
        SET status = 5
        WHERE activity_id = %s
        AND status = 1
        '''

        connect(sql, (activity_id,), False)

    def reactivate(activity_id):
        """Remove habit from the habit page"""

        sql = '''
        UPDATE activity_log 
        SET status = 1
        WHERE activity_id = %s
        AND status = 5
        '''

        connect(sql, (activity_id,), False)

    def update_date(activity_id, date):
        """Update the category name in the category table"""

        sql = """
        UPDATE activity_log
        SET date1 = %s
        WHERE activity_id = %s
        AND status = 1
        """

        connect(sql, (date, activity_id,), False)

    def update_time(activity_id, start_time, end_time):
        """Update event start/end time in the activity_log table"""

        sql = """
        UPDATE activity_log
        SET start_time = %s, end_time = %s
        WHERE activity_id = %s
        AND status = 1
        """

        connect(sql, (start_time, end_time, activity_id,), False)



