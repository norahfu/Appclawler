#!/usr/bin/env python
#coding=utf-8
__author__ = 'Norah'

import copy
import MySQLdb
from datetime import datetime

####################################################
def transV(values):
    #return [isinstance(v, basestring) and "'%s'" % v or v for v in values]
    return [isinstance(v, basestring) and "'%s'" % MySQLdb.escape_string(v) or v for v in values]

def joinKV(keys, values):
    return ["`%s`=%s" % (keys[i], values[i]) for i in xrange(len(keys))]



####################################################
# 建立数据库连接
def getConn(dbname):
    import ConfigParser
    cf = ConfigParser.ConfigParser()
    cf.read("../conf/db.conf")

    conn = MySQLdb.connect(
        host = cf.get(dbname, "host"),
        port = int(cf.get(dbname, "port")),
        user = cf.get(dbname, "user"),
        passwd = cf.get(dbname, "passwd"),
        db = cf.get(dbname, "db"))
    return conn


def getConnScoreDB():
    import ConfigParser
    cf = ConfigParser.ConfigParser()
    cf.read("../conf/db.conf")

    conn = MySQLdb.connect(
        host = cf.get("scoredb", "host"),
        port = int(cf.get("scoredb", "port")),
        user = cf.get("scoredb", "user"),
        passwd = cf.get("scoredb", "passwd"),
        db = cf.get("scoredb", "db"))
    return conn


####################################################
# 执行sql
def sqlExecute(sql, conn=None):
    try:
        inner_conn = False
        if not conn:
            conn = getConnScoreDB()
            inner_conn = True
        cur = conn.cursor()
        cur.execute(u'SET autocommit = 0;')
        cur.execute(u'SET NAMES utf8;')
        cur.execute(u'SET CHARACTER SET utf8;')
        cur.execute(u'SET character_set_connection=utf8;')
        #sql = sql.replace("\\", "\\\\")
        sql = sql.encode('utf-8')
        #print sql, '====sql'
        cur.execute(sql)
        results = [list(l) for l in cur.fetchall()]

        conn.commit()
        cur.close()
        if inner_conn:
            conn.close()

        #print results, '===result'
        if any(results):
            return results

        return []

    except Exception as e:
        print "Exception", e
        return []


####################################################
# 写mysql，更新已存在的记录
def updateRecord(measures, dimensions, table, conn=None):
    curTime = "%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    measures['modify_time'] = curTime

    _dimensions = joinKV(dimensions.keys(), transV(dimensions.values()))
    _dimensions = u"WHERE %s" % " AND ".join(_dimensions)
    _measures = joinKV(measures.keys(), transV(measures.values()))
    _measures = u"%s" % ", ".join(_measures)

    sql = u'''
            UPDATE `%s` SET %s %s;''' % (\
            table, _measures, _dimensions)

    sqlExecute(sql, conn=conn)


####################################################
# 写mysql，插入新记录
def insertRecord(measures, dimensions, table, conn=None):
    curTime = "%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    measures['create_time'] = curTime
    measures['modify_time'] = curTime

    _measures = copy.deepcopy(measures)
    _measures.update(dimensions)

    keys = u", ".join(_measures.keys())
    values = u", ".join(['%s'%v for v in transV(_measures.values())])

    sql = r'''
            INSERT INTO `%s` (%s) VALUES (%s);''' % (\
            table, keys, values)
    sqlExecute(sql, conn=conn)

####################################################
# 读mysql，查询记录
def getRecord(dimensions, table, conn=None):
    _dimensions = joinKV(dimensions.keys(), transV(dimensions.values()))
    _dimensions = u"WHERE %s" % " AND ".join(_dimensions)

    sql = r'''
            select * from `%s` %s;''' % (\
            table, _dimensions)
    return sqlExecute(sql, conn=conn)


####################################################
# 写mysql，更新已存在的记录或者插入新记录
def loadRecord(measures, dimensions, table, conn=None):
    #print "][", measures, dimensions, table, conn
    if getRecord(dimensions, table, conn=conn):
        updateRecord(measures, dimensions, table, conn=conn)
    else:
        insertRecord(measures, dimensions, table, conn=conn)

####################################################
# 写mysql，更新已存在的记录或者插入新记录
def getRecordId(dimensions, table, conn=None):

    _dimensions = joinKV(dimensions.keys(), transV(dimensions.values()))
    _dimensions = u"WHERE %s" % " AND ".join(_dimensions)

    sql_select = r'''
            select distinct id from `%s` %s;''' % (\
            table, _dimensions)
    ret = sqlExecute(sql_select , conn=conn)

    if not ret:
       insertRecord({}, dimensions, table, conn=conn)
       ret = sqlExecute(sql_select , conn=conn)

    if ret:
        return ret[0][0]
    else:
        return None


if "__main__" == __name__:
    pass

