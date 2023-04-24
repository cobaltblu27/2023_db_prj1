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
