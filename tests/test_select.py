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
  values("00", "Alice", "Millennium", 2020-01-01);
insert into student (id, name, school_name, created_at)
  values("04", "Yuzu", "Millennium", 2000-01-01);
insert into student (id, name, school_name, created_at)
  values("08", "Noah", "Millennium", 2010-01-01);
insert into student (id, name, school_name, created_at)
  values("michael", "Mika", "Trinity", 2005-01-01);
insert into student (id, name, school_name, created_at)
  values("prr", "Hifumi", "Trinity", 2015-01-01);
"""


def test_select(capfd):
    run(create_school)
    select_script = """
    select * from student as st, school
        where st.school_name = school.name and (
            st.created_at < 2008-01-01 and
            (not st.created_at < 1999-01-01) or st.name = 'Alice'
        );
    """
    capfd.readouterr()
    run(select_script)
    out, err = capfd.readouterr()
    assert out.count("Alice") == 1
    assert out.count("Yuzu") == 1
    assert out.count("Mika") == 1
    assert "Hifumi" not in out
    assert "Noah" not in out


