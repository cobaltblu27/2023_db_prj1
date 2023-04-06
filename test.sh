#!/bin/sh
source venv/bin/activate

python run.py -t \
"create table student (
  id INT not null, name char(32) not null,
  school_name char(16),
  created_at date,
  primary key (id, name),
  foreign key (school_name) references school(name)
);
explain student;"