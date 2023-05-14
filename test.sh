#!/bin/sh
source venv/bin/activate

rm -rf DB

python run.py -t "
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
  \"Millennium\",
  2019-01-01
);
insert into school values(
  \"Trinity\",
  1980-01-01
);
insert into student (id, name, school_name, created_at)
  values(\"00\", \"Alice\", \"Millennium\", 2020-01-01);
insert into student (id, name, school_name, created_at)
  values(\"04\", \"Yuzu\", \"Millennium\", 2000-01-01);
insert into student (id, name, school_name, created_at)
  values(\"08\", \"Noah\", \"Millennium\", 2010-01-01);
insert into student (id, name, school_name, created_at)
  values(\"michael\", \"Mika\", \"Trinity\", 2005-01-01);
insert into student (id, name, school_name, created_at)
  values(\"prr\", \"Hifumi\", \"Trinity\", 2015-01-01);

insert into student (id, name, school_name, created_at)
  values(\"r\", \"Rabu\", \"Millennium\", 1990-01-01);
"
python run.py -t "
    select st.name as name, school.name, club.name, st.id as S_ID from student as st, school, club, apply
        where st.school_name = school.name and apply.s_id = st.id and apply.c_id = club.id and (
            club.name = "GameDev" and (not st.created_at < 2010-01-01 or 1 = 0) and st.created_at <= 2020-01-01
        );
"
