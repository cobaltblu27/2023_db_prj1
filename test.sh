#!/bin/sh
source venv/bin/activate

rm -rf DB

python run.py -t "
create table school (
  name char(16) not null,
  created_at date,
  primary key (name)
);
create table student (
  id INT not null, name char(32) not null,
  school_name char(16) not null,
  created_at date,
  primary key (id, name),
  foreign key (school_name) references school(name)
);
"

python run.py -t "
show tables;
explain school;
explain student; 
"