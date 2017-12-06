import os
import subprocess
import psycopg2
#import snowflake.connector

def process_table(cur, prefix, suffix, type):
   table = "{0}_{1}".format(prefix, suffix)
   cur.execute("""drop table if exists {0}""".format(table))
   q = """
create table {0} (
  t timestamp,
  {1} {2}
)
""".format(table, suffix, type)
#   print q
   cur.execute(q)
   file = "{0}.{1}.tsv".format(prefix, suffix)
#   print "Loading {0} from {1}".format(table, file)
   f = open(file, 'r')
   cur.copy_from(f, table)
   f.close()
#   cur.execute("""PUT file://{0} @%{1}""".format(file, table))
#   cur.execute("""COPY INTO {0}""".format(table))

def add_melkopname(conn, cur, id, prefix):
    cur.execute("""
insert into melkopname
select '{0}', t1.t, t1.soll, t2.soll_rm, t3.abruf
from {1}_soll t1,
     {1}_soll_rm t2,
     {1}_abruf t3
where t1.t = t2.t and t2.t = t3.t
""".format(id, prefix))
    conn.commit()

def add_wateropname(conn, cur, id, prefix):
    cur.execute("""
insert into wateropname
select '{0}', t1.t, t1.daytikscounter, t2.tiks
from {1}_daytikscounter t1,
     {1}_tiks t2
where t1.t = t2.t
""".format(id, prefix))
    conn.commit()

def add_gewicht(conn, cur, id, prefix):
    cur.execute("""
insert into gewicht
select '{0}', t1.t, t1.wcorr
from {1}_wcorr t1
""".format(id, prefix))
    conn.commit()

try:
   conn = psycopg2.connect("dbname='' user='' host='' password=''")
#   conn = snowflake.connector.connect(user='', password='', account='')
except:
    print "I am unable to connect to the database"
cur = conn.cursor();
#cur.execute("use warehouse chosiaposia")
#cur.execute("use sdf.public")

nsuccess = 0
nfailure = 0

cur.execute("""drop table if exists melkopname""")
cur.execute("""
create table melkopname(
  id varchar(20),
  t timestamp,
  soll float,
  soll_rm float,
  abruf float
)""")
cur.execute("""drop table if exists wateropname""")
cur.execute("""
create table wateropname(
  id varchar(20),
  t timestamp,
  daytikscounter int,
  tiks int
)""")
cur.execute("""drop table if exists gewicht""")
cur.execute("""
create table gewicht(
  id varchar(20),
  t timestamp,
  wcorr float
)""")

conn.commit()

for root, dirs, files in os.walk("dairycampus/category5"):
   for name in dirs:
       if name == "measurements":
          continue
       os.chdir(os.path.join(root, name))
       print "Processing " + name + "...";
       os.chdir("measurements")
       
       try:
           prefix = "Melkopname_ForsterCANBUS"
           for suffix, type in [["soll", "float"], ["soll_rm", "float"], ["abruf", "float"]]:
               process_table(cur, prefix, suffix, type)
           add_melkopname(conn, cur, name, prefix)
           prefix = "WaterOpname_ATELCONDIS250"
           for suffix, type in [["daytikscounter", "int"], ["tiks", "int"]]:
               process_table(cur, prefix, suffix, type)
           add_wateropname(conn, cur, name, prefix)
           prefix = "Gewicht_Gallagher"
           for suffix, type in [["wcorr", "float"]]:
               process_table(cur, prefix, suffix, type)
           add_gewicht(conn, cur, name, prefix)

           nsuccess = nsuccess + 1
       except IOError as e:
           print "Unable to open a file in directory {0}: {1}".format(name, e.strerror)
           nfailure = nfailure + 1
       except psycopg2.DataError as e:
           print "Error loading table in directory {0}".format(name)
           conn.rollback()
           nfailure = nfailure + 1
       os.chdir("../../../..")

print "{0} successes, {1} failures".format(nsuccess, nfailure)
