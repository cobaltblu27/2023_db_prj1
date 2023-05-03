#!/bin/sh
source venv/bin/activate

python run.py -t "
select st.name from student as st, school
where created_at < 2008-01-01 and
(not created_at < "1999-01-01") or st.name = 'Alice';"