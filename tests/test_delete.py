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
insert into school (name, created_at) values(
  "Millennium",
  2019-01-01
);
insert into school values(
  "Trinity",
  1980-01-01
);
insert into student (id, name, school_name, created_at)
  values("00", "Alice", "Millennium", 1980-01-01);
"""


def test_delete(capfd):
    run(create_school)
    run("""delete from school where created_at < 2000-01-01;""")
    capfd.readouterr()
    run("select * from school;")
    out, _ = capfd.readouterr()
    assert "Millennium" in out
    assert "Trinity" not in out


def test_no_such_table():
    run(create_school)
    with pytest.raises(NoSuchTableError):
        run("""delete from foo where created_at < 2000-01-01;""")


def test_no_such_table_where():
    run(create_school)
    with pytest.raises(WhereTableNotSpecified):
        run("""delete from school where foo.created_at < 2000-01-01;""")


def test_no_such_column_where():
    run(create_school)
    with pytest.raises(WhereColumnNotExist):
        run("""delete from school where school.foo < 2000-01-01;""")


def test_delete_all(capfd):
    run(create_school)
    run("""delete from student;""")
    run("""delete from school;""")
    capfd.readouterr()
    run("select * from school;")
    out, _ = capfd.readouterr()
    assert "Millennium" not in out
    assert "Trinity" not in out


def test_delete_integrity():
    run(create_school)
    with pytest.raises(DeleteReferentialIntegrityPassed):
        run("delete from school where name = 'Millennium';")

