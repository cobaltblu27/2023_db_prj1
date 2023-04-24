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
"""


def test_drop_table(capfd):
    run(create_school)
    run("drop table school;")
    capfd.readouterr()
    run("show tables;")
    out, err = capfd.readouterr()
    assert "school" not in out


def test_drop_no_such_tbl():
    with pytest.raises(NoSuchTable):
        run("drop table school;")


def test_drop_referenced_tbl():
    run(create_school)
    run("""
    create table student(
      name char(16),
      school_name char(16),
      primary key (name),
      foreign key (school_name) references school(name)
    );
    """)
    with pytest.raises(DropReferencedTableError):
        run("drop table school;")


def test_drop_erases_rows(capfd):
    run(create_school)
    run("""insert into school values("Abydos", 2019-01-01);""")
    run("drop table school;")
    run(create_school)
    capfd.readouterr()
    run("select * from school;")
    out, err = capfd.readouterr()
    assert "Abydos" not in out

