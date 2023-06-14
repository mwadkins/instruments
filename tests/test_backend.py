#!/prj/qct/coredev/hexagon/sitelinks/arch/bin/pkw_python3.6.0
"""
A module for the backend database code
pytest will run all tests (functions that start w/ test_) in this module in order
"""
# pylint: disable=wrong-import-position
import logging

import backend
import utils

BDB = None


def setup():
    """
    configure the logger
    NOTE: Logging is weird!  This must be done before
      any logging calls
    """
    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # set formatter in handler
    handler.setFormatter(formatter)

    # add handler to logger
    logger.addHandler(handler)

    # create a db
    debug = True
    dbfile = "test_basic.db"
    # start with a fresh db each time
    utils.run_cmd(f"rm -rf {dbfile}")
    # pylint: disable=global-statement
    global BDB
    BDB = backend.BackendDb(dbfile, debug)


def test_add_students():
    """add a few students"""
    # add a new student to the students table in the db
    firstname = "Logan"
    lastname = "Reid"
    dob = "04/19/1998"
    address = "14304 Laurinburg"
    city = "Austin"
    state = "TX"
    zipcode = "78717"
    phone = "512-716-0011"
    note = "needs to practice more"
    BDB.add_or_update_student(firstname, lastname, dob, address, city, state, zipcode, phone, note)

    # add a new student to the students table in the db
    firstname = "Nikolai"
    lastname = "Richards"
    dob = "07/09/2002"
    address = "14905 Solera"
    city = "Austin"
    state = "TX"
    zipcode = "78717"
    phone = "512-716-0011"
    note = ""
    BDB.add_or_update_student(firstname, lastname, dob, address, city, state, zipcode, phone, note)

    # read the db
    ret = BDB.read_table("students")
    for student_row in ret:
        print(str(student_row))

    # check the students table
    ret = BDB.read_table("students")
    print(str(ret))
    print(str(type(ret)))
    assert ret[0] == (
        1,
        "Logan",
        "Reid",
        "04/19/1998",
        "14304 Laurinburg",
        "Austin",
        "TX",
        "78717",
        "512-716-0011",
        "needs to practice more",
    )
    assert ret[1] == (
        2,
        "Nikolai",
        "Richards",
        "07/09/2002",
        "14905 Solera",
        "Austin",
        "TX",
        "78717",
        "512-716-0011",
        "",
    )


def test_add_instruments():
    """
    add a few instruments
    """
    # add a new instrument to the instruments table in the db
    instr_type = "flute"
    serial_num = "12345"
    maker = "bach"
    note = "needs tuning"
    BDB.add_or_update_instrument(instr_type, serial_num, maker, note)

    # add a new instrument to the instruments table in the db
    instr_type = "trumpet"
    serial_num = "986"
    maker = "yamaha"
    note = ""
    BDB.add_or_update_instrument(instr_type, serial_num, maker, note)

    # read the db
    ret = BDB.read_table("instruments")
    for instrument_row in ret:
        print(str(instrument_row))

    # check the instruments table
    ret = BDB.read_table("instruments")
    print(str(ret))
    print(str(type(ret)))
    assert ret[0] == (1, "flute", "12345", "bach", "needs tuning")
    assert ret[1] == (2, "trumpet", "986", "yamaha", "")


def test_update_student():
    """update an existing student"""
    # do the update
    firstname = "Nikolai"
    lastname = "Richards"
    dob = "07/09/2002"
    address = "14905 Solera"
    city = "Austin"
    state = "TX"
    zipcode = "78717"
    phone = "512-716-0011"
    note = "making excellent progress"
    BDB.add_or_update_student(firstname, lastname, dob, address, city, state, zipcode, phone, note)
    # check the students table
    ret = BDB.read_table("students")
    print(str(ret))
    print(str(type(ret)))
    assert ret[0] == (
        1,
        "Logan",
        "Reid",
        "04/19/1998",
        "14304 Laurinburg",
        "Austin",
        "TX",
        "78717",
        "512-716-0011",
        "needs to practice more",
    )
    assert ret[1] == (
        2,
        "Nikolai",
        "Richards",
        "07/09/2002",
        "14905 Solera",
        "Austin",
        "TX",
        "78717",
        "512-716-0011",
        "making excellent progress",
    )


def test_update_instruments():
    """update an existing instrument"""
    # do the update
    instr_type = "trumpet"
    serial_num = "986"
    maker = "yamaha"
    note = "out for repair"
    BDB.add_or_update_instrument(instr_type, serial_num, maker, note)
    # check the instruments table
    ret = BDB.read_table("instruments")
    print(str(ret))
    print(str(type(ret)))
    assert ret[0] == (1, "flute", "12345", "bach", "needs tuning")
    assert ret[1] == (2, "trumpet", "986", "yamaha", "out for repair")
