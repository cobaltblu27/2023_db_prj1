#!/bin/sh
source venv/bin/activate

rm -rf DB

python run.py -t "
create table school (
  name char(16),
  created_at date,
  primary key (name)
);
insert into school values(
  \"Abydos\",
  2019-01-01
);
select * from school;
insert into school (name, created_at) values(
  \"Trinity\",
  1980-01-01
);
select * from school;
"