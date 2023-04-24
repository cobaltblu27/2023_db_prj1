import pytest

from src.errors import *
from tests.common import run, pytest_reset


@pytest.fixture(autouse=True)
def before_each():
    pytest_reset()


create_school = """
create table school (
  name char(16),
  created_at date,
  primary key (name)
);
create table student (
  id int, name char(32),
  school_name char(16) not null,
  created_at date,
  primary key (id, name),
  foreign key (school_name) references school(name)
);
"""


def test_create_table():
    run(create_school)


def test_foreign_key_composite():
    run(create_school)
    create_grade = """
    create table grade (
      name char(32),
      id int,
      primary key (name),
      foreign key (id, name) references student(id, name)
    ); 
    """
    run(create_grade)


def test_duplicate_cols():
    sql = """
create table school (
  name char(16),
  created_at date,
  created_at date,
  primary key (name)
);
"""
    with pytest.raises(DuplicateColumnDefError):
        run(sql)


def test_duplicate_pkeys():
    sql = """
    create table school (
      name char(16),
      created_at date,
      primary key (name),
      primary key (name)
    );
    """
    with pytest.raises(DuplicatePrimaryKeyDefError):
        run(sql)


def test_foreign_key_type_allow_nullable():
    run(create_school)
    foreign_key_sql_wrong_type_nullable = """
    create table club (
      name char(32),
      school_name char(16),
      primary key (name),
      foreign key (school_name) references school(name)
    ); 
    """
    run(foreign_key_sql_wrong_type_nullable)


def test_foreign_key_type_length():
    run(create_school)
    foreign_key_sql_wrong_type_length = """
    create table club (
      name char(32),
      school_name char(123),
      primary key (name),
      foreign key (school_name) references school(name)
    ); 
    """
    with pytest.raises(ReferenceTypeError):
        run(foreign_key_sql_wrong_type_length)


def test_foreign_key_type_wrong_col():
    run(create_school)
    foreign_key_sql_wrong_col = """
    create table club (
      name char(32),
      school_name char(16) not null,
      primary key (name),
      foreign key (school_name) references school(created_at)
    ); 
    """
    with pytest.raises(ReferenceNonPrimaryKeyError):
        run(foreign_key_sql_wrong_col)


def test_foreign_key_type_not_pkey():
    run(create_school)

    foreign_key_sql_wrong_pair = """
    create table grade (
      name char(32),
      primary key (name),
      foreign key (name) references student(name)
    ); 
    """
    with pytest.raises(ReferenceNonPrimaryKeyError):
        run(foreign_key_sql_wrong_pair)


def test_foreign_key_type_no_col():
    run(create_school)
    foreign_key_sql_col_non_exists = """
    create table grade (
      name char(32),
      primary key (name),
      foreign key (name) references student(foo)
    ); 
    """
    with pytest.raises(ReferenceColumnExistenceError):
        run(foreign_key_sql_col_non_exists)


def test_foreign_key_no_table():
    foreign_key_sql_tb_non_exists = """
create table student (
  id int not null, name char(32) not null,
  school_name char(16) not null,
  created_at date,
  primary key (id, name),
  foreign key (school_name) references school(name)
);
    """
    with pytest.raises(ReferenceTableExistenceError):
        run(foreign_key_sql_tb_non_exists)


def test_dup_table():
    run(create_school)
    sql = """
       create table school (
         name char(16),
         created_at date,
         primary key (name)
       );
       """
    with pytest.raises(TableExistenceError):
        run(sql)


def test_pkey_non_exists():
    no_pkey = """
create table student (
  id int not null,
  primary key (name)
);
    """
    with pytest.raises(NonExistingColumnDefError):
        run(no_pkey)


def test_fkey_non_exists():
    run(create_school)
    no_pkey = """
    create table club (
      name char(32),
      primary key (name),
      foreign key (school_name) references school(name)
    ); 
    """
    with pytest.raises(NonExistingColumnDefError):
        run(no_pkey)


def test_char_len():
    sql = """
       create table school (
         name char(0),
         primary key (name)
       );
       """
    with pytest.raises(CharLengthError):
        run(sql)


def test_table_name_case_insensitivity():
    run(create_school)
    sql = """
    create table SCHOOL (
     name char(0),
     primary key (name)
    );
    """
    with pytest.raises(TableExistenceError):
        run(sql)
