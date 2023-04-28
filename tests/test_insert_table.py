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
  id int not null, name char(32) not null,
  school_name char(16) not null,
  created_at date,
  primary key (id, name),
  foreign key (school_name) references school(name)
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
    insert_sql = """
    insert into school (name, created_at) values(
        "Abydos",
        2019-01-01
    );
    insert into school values(
        "Trinity",
        1980-01-01
    );
    """
    run(insert_sql)
    out, _ = capfd.readouterr()
    assert "The row is inserted" in out

    run("select * from school;")
    out, _ = capfd.readouterr()
    assert "Abydos" in out
    assert "Trinity" in out


def test_insert_no_table(capfd):
    run(create_school)
    insert_sql = """
    insert into club (name) values(
        "game dev"
    );
    """
    with pytest.raises(NoSuchTable):
        run(insert_sql)
