import os
import psycopg2
import pymongo
from jira import JIRA
from pymongo import MongoClient

def indexing():
    service = os.environ["SERVICE"]
    admin_pwd = os.environ["ADMIN_PWD"]
    database = os.environ["DATABASE"]
    collection = os.environ["COLLECTION"]
    new_index = os.environ["NEW_INDEX"]
    issue_key = os.environ["ISSUE_KEY"]
    jira_user = os.environ["ISSUE_KEY"]
    jira_token = os.environ["JIRA_TOKEN"]
    jira_header = {"server": "https://XXXXX.atlassian.net"}
    jenkins_build_url = os.environ["BUILD_URL"] + "console"

    con = psycopg2.connect(database="DATABASE", user="USER", password=admin_pwd, host="HOST", port="5432")
    cur = con.cursor()
    cur.execute("SELECT ips FROM mongo_hosts WHERE service = '" + service + "'")
    ips = cur.fetchone()
    ip = ips[0]
    cur.execute("SELECT password FROM users WHERE username = 'USER'")
    pwds = cur.fetchone()
    pwd = pwds[0]
    client = MongoClient("mongodb://USER:" + pwd + "@" + ip + "/" + database + "?replicaSet=rs-" + database + "-query")
    db_con = client[database]

    jira_con = JIRA(jira_header, basic_auth=(jira_user, jira_token))
    issue = jira_con.issue(issue_key)

    to_inprogress = jira_con.transition_issue(issue, '91')
    print(to_inprogress)

    try:
        jira_con.add_comment(issue, jenkins_build_url)
        index_before = db_con[collection].index_information()
        print("index before changed :\n", index_before, "\n")
        changes = db_con[collection].create_index([(new_index, pymongo.ASCENDING)], background=True)
        print("index added : ", changes, "\n")
        index_after = db_con[collection].index_information()
        print("index after changed :\n", index_after, "\n")

        to_done = jira_con.transition_issue(issue, '41')
        print(to_done)

    except:
        print("pipeline failed")
        to_done = jira_con.transition_issue(issue, '61')
        print(to_done)

indexing()
