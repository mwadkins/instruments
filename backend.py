#!/usr/local/bin/python3

"""
A module for the backend database code

Notes: Example command line usage of db:
 % sqlite3 test_basic.db
SQLite version 3.8.3.1 2014-02-11 14:52:19
Enter .help for instructions
Enter SQL statements terminated with a ;
sqlite> .tables
instruments  inventory    students
sqlite> .schema instruments
CREATE TABLE instruments (id   INTEGER PRIMARY KEY AUTOINCREMENT,
  type   CHAR(50), serial_num CHAR(50), maker CHAR(50), notes  CHAR(50) );
sqlite> .quit

"""
import logging
import os
import re
import sqlite3
import sys


class BackendDb:
    """
    A class for interacting with the database
    """

    def __init__(self, dbfile, debug):
        """
        constructor
        """
        self.dbfile = dbfile
        self.debug = debug
        self.create_tables()
        logging.debug("sqlite db: %s", self.dbfile)

    def execute_stmt(self, stmt, many=None):
        """
        wrapper for executing sql statement
        """
        if self.debug:
            logging.debug("execute_stmt: %s", stmt)
            if many:
                logging.debug(many)

        retry = 3
        while retry:
            retry -= 1
            # connect to db
            conn = sqlite3.connect(self.dbfile)
            cur = conn.cursor()
            result = None
            try:
                if many:
                    cur.executemany(stmt, many)
                    conn.commit()
                else:
                    cur.execute(stmt)
                    conn.commit()
                    if stmt.lstrip().upper().startswith("SELECT"):
                        result = cur.fetchall()
                retry = 0
            except sqlite3.Error as err:
                logging.fatal("backend.py execute_stmt: Error: %s", err.args[0])
                if re.search("database is locked", err.args[0]):
                    # try to repair the database
                    cmd = "cp " + self.dbfile + " saved && rm " + self.dbfile
                    cmd += " && mv saved " + self.dbfile
                    os.system(cmd)
                sys.exit(1)
        conn.close()
        logging.debug("Result: %s", str(result))
        return result

    def create_inventory_table(self):
        """
        create inventory table if it doesn't already exist
        This is a mapping of student_id <-> instrument_id
        """
        stmt = "CREATE TABLE IF NOT EXISTS inventory ("
        stmt += " id        INTEGER PRIMARY KEY AUTOINCREMENT,"
        stmt += " instrument_id  INTEGER,"
        stmt += " student_id  INTEGER,"
        stmt += " notes      CHAR(200)"
        stmt += ")"
        self.execute_stmt(stmt)

    def create_instrument_table(self):
        """
        create instrument table if it doesn't already exist
        """
        stmt = "CREATE TABLE IF NOT EXISTS instruments ("
        stmt += " id         INTEGER PRIMARY KEY AUTOINCREMENT,"
        stmt += " type       CHAR(50),"  # ex: flute
        stmt += " serial_num CHAR(50),"
        stmt += " maker      CHAR(50),"  # ex: bach
        stmt += " notes      CHAR(200)"
        stmt += ")"
        self.execute_stmt(stmt)

        # create a unique index on serial num
        #  so that our insert or update will work and we can never have the
        #  same serial numbered instrument in more than once in the db
        stmt = "CREATE UNIQUE INDEX serial_number on instruments(serial_num)"
        self.execute_stmt(stmt)

    def create_student_table(self):
        """
        create student table if it doesn't already exist
        """
        stmt = "CREATE TABLE IF NOT EXISTS students ("
        stmt += " id         INTEGER PRIMARY KEY AUTOINCREMENT,"
        stmt += " firstname  CHAR(50),"
        stmt += " lastname   CHAR(50),"
        stmt += " dob        DATETIME,"
        stmt += " address    CHAR(50),"
        stmt += " city       CHAR(50),"
        stmt += " state      CHAR(50),"
        stmt += " zip        CHAR(50),"
        stmt += " phone      CHAR(50),"
        stmt += " notes      CHAR(200)"
        stmt += ")"
        self.execute_stmt(stmt)

        # create a unique index on firstname/lastname/dob
        # so that our insert or update will work and we can never have the
        # same student (first, last, dob) in more than once in the db
        stmt = "CREATE UNIQUE INDEX first_last_dob on students (firstname, lastname,dob)"
        self.execute_stmt(stmt)

    def add_or_update_instrument(self, itype, serial_num, maker, notes):
        """
        add an instrument if it doesn't already exist (based on unique
        serial_num).  If it already just update it.
        """
        values = [itype, serial_num, maker, notes]
        # first check if this serial number/instrument is already in the db
        rows = self.execute_stmt("select id from instruments where serial_num='" + serial_num + "'")
        if rows:
            # it is, so we will just update it
            inst_id = rows[0][0]  # first row, first column
            values = [inst_id, itype, serial_num, maker, notes]
            stmt = "REPLACE into instruments (id, type, serial_num, maker, notes) values (?,?,?,?,?)"
        else:
            # it is not, so we will add it
            stmt = "INSERT into instruments (type, serial_num, maker, notes) values (?,?,?,?)"
        # execute the query
        self.execute_stmt(stmt, [values])

    def add_or_update_student(self, firstname, lastname, dob, address, city, state, zipcode, phone, notes):
        # pylint: disable=too-many-arguments
        """
        add a student if they don't already exist (based on unique
        firstname, lastname, dob).  If they already exist, just update info.
        """
        values = [firstname, lastname, dob, address, city, state, zipcode, phone, notes]
        # first check if this student is already in the db
        stmt = "select id from students where firstname='" + firstname + "'"
        stmt += " AND lastname='" + lastname + "'"
        stmt += " AND dob='" + dob + "'"
        rows = self.execute_stmt(stmt)
        if rows:
            # they are, so we will just update it
            student_id = rows[0][0]  # first row, first column
            values = [student_id, firstname, lastname, dob, address, city, state, zipcode, phone, notes]
            stmt = "REPLACE into students (id, firstname, lastname, dob, address, city, state, zip, phone, notes)"
            stmt += " values (?,?,?,?,?,?,?,?,?,?)"
        else:
            # they are not, so we will add it
            stmt = "INSERT into students (firstname, lastname, dob, address, city, state, zip, phone, notes)"
            stmt += " values (?,?,?,?,?,?,?,?,?)"
        # execute the query
        self.execute_stmt(stmt, [values])

    def create_tables(self):
        """
        create all tables
        """
        self.create_instrument_table()
        self.create_student_table()
        self.create_inventory_table()

    def read_table(self, table):
        """
        read the entire db
        """

        # query the database
        stmt = "select * from " + table
        result = self.execute_stmt(stmt)

        if not result:
            logging.error("No results found")
            logging.error("sqlite3  %s", self.dbfile)
            logging.error(stmt)

        return result

    def add_or_update_inventory(self, instrument_id, student_id, notes):
        """
        update the db: expects a list of lists where each entry is in this format:
          (instrument_id, student_id, status_id, notes)
        """
        values = [instrument_id, student_id, notes]
        # write to the database
        # pylint: disable=line-too-long
        stmt = "INSERT into inventory (instrument_id, student_id, notes) values (?,?,?,?,?)"
        self.execute_stmt(stmt, values)
