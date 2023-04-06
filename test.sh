#!/bin/sh
source venv/bin/activate

python run.py -t "create table foo (id INT not null, name char(32) not null,d date, primary key (id, name)); explain foo;"