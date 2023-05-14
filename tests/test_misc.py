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


def test_desc(capfd):
    run(create_school)
    capfd.readouterr()
    run("desc student;")
    out, err = capfd.readouterr()
    assert "student" in out


def test_desc_none():
    run(create_school)
    with pytest.raises(NoSuchTableError):
        run("desc asdf;")


def test_select_no_table():
    run(create_school)
    with pytest.raises(SelectTableExistenceError):
        run("select * from club;")
