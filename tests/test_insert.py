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
  id char(10) not null,
  name char(20) not null,
  school_name char(16) not null,
  created_at date,
  primary key (id),
  foreign key (school_name) references school(name)
);
create table club (
  id int not null,
  name char (20),
  capacity int,
  primary key (id)
);
create table ref (
  id int,
  foreign key (id) references club (id)
);
create table apply (
  s_id char (10) not null,
  l_id int not null,
  apply_date date,
  primary key (s_id, l_id),
  foreign key (s_id) references student (id),
  foreign key (l_id) references club (id)
);
"""

create_prereq = """
create table students (
 id char (10) not null,
 name char (20),
 primary key (id)
);
create table lectures (
 id int not null,
 name char (20),
 capacity int,
 primary key (id)
);
create table ref (
 id int,
 foreign key (id) references lectures (id)
);
create table apply (
 s_id char (10) not null,
 l_id int not null,
 apply_date date,
 primary key (s_id, l_id),
 foreign key (s_id) references students (id),
 foreign key (l_id) references lectures (id)
);
"""


def test_prereq():
    run(create_prereq)


# 1-2에선 유효한 입력만 가정
def test_insert_table(capfd):
    run(create_school)
    run("""
    insert into school (name, created_at) values(
        "Abydos",
        2019-01-01
    );
    """)
    out, _ = capfd.readouterr()
    assert "The row is inserted" in out

    run("""
    insert into school values(
        "Trinity",
        1980-01-01
    );
    """)
    out, _ = capfd.readouterr()
    assert "The row is inserted" in out

    run("select * from school;")
    out, _ = capfd.readouterr()
    assert "Abydos" in out
    assert "Trinity" in out


def test_insert_no_table(capfd):
    run(create_school)
    insert_sql = """
    insert into foo (name) values(
        "bar"
    );
    """
    with pytest.raises(NoSuchTableError):
        run(insert_sql)


def test_insert_type_mismatch():
    run(create_school)
    insert_sql = """
    insert into school (name, created_at)
        values(123, 1980-01-01);
    """
    with pytest.raises(InsertTypeMismatchError):
        run(insert_sql)


def test_insert_attr_mismatch():
    run(create_school)
    insert_sql = """insert into school values("Trinity");"""
    with pytest.raises(InsertTypeMismatchError):
        run(insert_sql)


def test_insert_attr_values_mismatch():
    run(create_school)
    insert_sql = """
    insert into school (name)
        values("Valkyrie", 1980-01-01);
    """
    with pytest.raises(InsertTypeMismatchError):
        run(insert_sql)


def test_insert_null_in_nonnull():
    run(create_school)
    insert_sql = """
    insert into student (id, name, created_at)
        values("mk", "Mika", 1980-01-01);
    """
    with pytest.raises(InsertColumnNonNullableError):
        run(insert_sql)


def test_insert_column_existence():
    run(create_school)
    insert_sql = """
    insert into student (id, name, school_name, created_at, str)
        values("39", "Mika", "Trinity", 1980-01-01, 99999);
    """
    with pytest.raises(InsertColumnExistenceError):
        run(insert_sql)


def test_insert_tuple_length_cutoff(capfd):
    run(create_school)
    insert_sql = """
    insert into school (name) values("0123456789abcdefg");
    """
    run(insert_sql)

    capfd.readouterr()
    run("select * from school;")
    out, _ = capfd.readouterr()
    assert "0123456789abcdef" in out
    assert "0123456789abcdefg" not in out


# def test_insert_pkey_dup():
#     run(create_school)
#     insert_sql = """insert into school values("Trinity");"""
#     run(insert_sql)
#     with pytest.raises(InsertDuplicatePrimaryKeyError):
#         run(insert_sql)
#
#
# def test_insert_ref_integrity_err():
#     run(create_school)
#     insert_sql = """
#     insert into student (id, name, school_name, created_at)
#         values(39, "Mika", "Trinity", 1980-01-01);
#     """
#     with pytest.raises(InsertReferentialIntegrityError):
#         run(insert_sql)
#
