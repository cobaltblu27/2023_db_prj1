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
  address char(64),
  phone_number char(64),
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
  c_id int not null,
  apply_date date,
  primary key (s_id, c_id),
  foreign key (s_id) references student (id),
  foreign key (c_id) references club (id)
);
insert into school (name, created_at) values(
  "Millennium",
  2019-01-01
);
insert into school values(
  "Trinity",
  1980-01-01
);
insert into club values(
  0, "GameDev", 4
);
insert into student (id, name, school_name, created_at)
  values("AL-1S", "Alice", "Millennium", 2020-01-01);
insert into student (id, name, school_name, created_at)
  values("Yz", "Yuzu", "Millennium", 2000-01-01);
insert into student (id, name, school_name, created_at)
  values("N", "Noah", "Millennium", 2010-01-01);
insert into student (id, name, school_name, created_at)
  values("Michael", "Mika", "Trinity", 2005-01-01);
insert into student (id, name, school_name, created_at)
  values("PRR", "Hifumi", "Trinity", 2015-01-01);
insert into student (id, name, school_name, created_at)
  values("null", "Himari", "Millenium", null);
  
insert into apply values("AL-1S", 0, 2023-05-05);
insert into apply (s_id, c_id) values("Yz", 0);
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


def test_select_2(capfd):
    run(create_school)
    select_script = """
    select st.name as name, school.name, club.name, st.id as S_ID from student as st, school, club, apply
        where st.school_name = school.name and apply.s_id = st.id and apply.c_id = club.id and (
            club.name = "GameDev" and (not st.created_at < 2010-01-01 or 1 = 0) and st.created_at <= 2020-01-01
        );
    """
    capfd.readouterr()
    run(select_script)
    out, err = capfd.readouterr()
    assert out.count("Alice") == 1
    assert "Yuzu" not in out
    assert "Mika" not in out
    assert "Hifumi" not in out
    assert "Noah" not in out

    assert "st.name" not in out
    assert "S_ID" in out


def test_select_3(capfd):
    run(create_school)
    select_script = """
    select st.name as name, school.name, club.name, st.id as S_ID from student as st, school, club, apply
        where st.school_name = school.name and apply.s_id = st.id and apply.c_id = club.id and (
            club.name = "GameDev" and apply.apply_date is not null
        );
    """
    capfd.readouterr()
    run(select_script)
    out, err = capfd.readouterr()
    assert out.count("Alice") == 1
    assert "Yuzu" not in out
    assert "Mika" not in out
    assert "Hifumi" not in out
    assert "Noah" not in out

    assert "st.name" not in out
    assert "S_ID" in out


def test_select_all(capfd):
    run(create_school)
    capfd.readouterr()
    run("select * from school, student;")
    out, _ = capfd.readouterr()
    assert out.count("Alice") == 2


def test_select_column_resolve_error():
    run(create_school)
    select_script = """
        select foo from student;
    """
    with pytest.raises(SelectColumnResolveError):
        run(select_script)


def test_null_comparison_unknown(capfd):
    run(create_school)
    select_script = """
    select * from student where name = 'Himari' and created_at = created_at;
    """
    capfd.readouterr()
    run(select_script)
    out, _ = capfd.readouterr()
    assert "Himari" not in out


def test_where_ambiguous(capfd):
    run(create_school)
    delete_script = """
    delete from apply;
    delete from school;
    delete from student;
    """
    select_script = """
    select * from school, student where created_at < 2000-01-01;
    """
    run(delete_script)
    with pytest.raises(WhereAmbiguousReference):
        run(select_script)

