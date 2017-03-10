#!/usr/bin/python

import os
import commands

CONTROLLER_HOSTNAME='controller'
ADMIN_PASS='123456'
MYSQL_PASS='123456'
GLANCE_PASS = '123456'
NOVA_PASS = '123456'
NEUTRON_PASS = '123456'
CINDER_PASS = '123456'

KEYSTONE_DBPASS = '123456'
GLANCE_DBPASS = '123456'
NOVAAPI_DBPASS = '123456'
NOVA_DBPASS = '123456'
NEUTRON_DBPASS = '123456'
CINDER_DBPASS = '123456'

dbopt = {
         "keystone":  [{"sysuser": "keystone",  "dbname": "keystone",  "dbpasswd": KEYSTONE_DBPASS,  "dbsync": "keystone-manage db_sync"}],
         "glance":    [{"sysuser": "glance",    "dbname": "glance",    "dbpasswd": GLANCE_DBPASS,    "dbsync": "glance-manage db_sync"}],
         "nova":      [
                       {"sysuser": "nova",      "dbname": "nova_api",  "dbpasswd": NOVAAPI_DBPASS,   "dbsync": "nova-manage api_db sync"},
                       {"sysuser": "nova",      "dbname": "nova",      "dbpasswd": NOVA_DBPASS,      "dbsync": "nova-manage db sync"}
                      ],
         "neutron":   [{"sysuser": "neutron",   "dbname": "neutron",   "dbpasswd": NEUTRON_DBPASS,   "dbsync": "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head"}],
         "cinder":    [{"sysuser": "cinder",    "dbname": "cinder",    "dbpasswd": CINDER_DBPASS,    "dbsync": "cinder-manage db sync"}]
        }

serviceopt ={
              "glance": [{"name":"glance",   "type":"image",    "description":"OpenStack Image",         "http":"http://%s:9292" % CONTROLLER_HOSTNAME}],
              "nova":   [{"name":"nova",     "type":"compute",  "description":"OpenStack Compute",       "http":"http://%s:8774/v2.1/%%\(tenant_id\)s" % CONTROLLER_HOSTNAME}],
              "neutron":[{"name":"neutron",  "type":"network",  "description":"OpenStack Networking",    "http":"http://%s:9696" % CONTROLLER_HOSTNAME}],
              "cinder": [
                         {"name":"cinder",   "type":"volume",   "description":"OpenStack Block Storage", "http":"http://%s:8776/v1/%%\(tenant_id\)s" % CONTROLLER_HOSTNAME},
                         {"name":"cinderv2", "type":"volumev2", "description":"OpenStack Block Storage", "http":"http://%s:8776/v2/%%\(tenant_id\)s" % CONTROLLER_HOSTNAME}
                        ]
             }

admin_env ={
             "OS_USERNAME": "admin",
             "OS_PASSWORD": ADMIN_PASS,
             "OS_PROJECT_NAME": "admin",
             "OS_USER_DOMAIN_NAME": "Default",
             "OS_PROJECT_DOMAIN_NAME": "Default",
             "OS_AUTH_URL": "http://%s:35357/v3" % CONTROLLER_HOSTNAME,
             "OS_IDENTITY_API_VERSION": "3",
             "OS_IMAGE_API_VERSION": "2"
           }

def exec_cmd(cmd):
    print "==>: " + cmd
    status, output = commands.getstatusoutput(cmd)
    if status != 0:
        raise Exception("[%s] \nCommand exec error: %s" % (cmd, output))

def create_db(dbs):
    for db in dbs:
        try:
            sql = "DROP DATABASE %s; " % db['dbname']
            cmd = "mysql -uroot -p%s -e \"%s\"" % (MYSQL_PASS, sql)
            exec_cmd(cmd)
        except Exception as e:
            pass

        sql = "CREATE DATABASE %s; " % db['dbname'] + \
              "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s'; " % (db['dbname'], db['sysuser'], db['dbpasswd']) + \
              "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s'" % (db['dbname'], db['sysuser'], db['dbpasswd'])
        cmd = "mysql -uroot -p%s -e \"%s\"" % (MYSQL_PASS, sql)
        exec_cmd(cmd)

        cmd = "su -s /bin/sh -c \"%s\" %s" % (db['dbsync'], db['sysuser'])
        exec_cmd(cmd)


def keystone_init():
    cmd = "keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone; " + \
          "keystone-manage credential_setup --keystone-user keystone --keystone-group keystone; " + \
          "keystone-manage bootstrap --bootstrap-password %s " % ADMIN_PASS + \
          "--bootstrap-admin-url http://%s:35357/v3/ " % CONTROLLER_HOSTNAME + \
          "--bootstrap-internal-url http://%s:35357/v3/ " % CONTROLLER_HOSTNAME + \
          "--bootstrap-public-url http://%s:5000/v3/ " % CONTROLLER_HOSTNAME + \
          "--bootstrap-region-id RegionOne"
    exec_cmd(cmd)

def create_project_service():
    cmd = "openstack project create --domain default --description \"Service Project\" service"
    exec_cmd(cmd)

def create_user_and_service(user,passwd):
    def __create_service(services):
        for service in services:
            cmd = "openstack service create --name %s --description \"%s\" %s; " %(service['name'], service['description'],service['type']) + \
                  "openstack endpoint create --region RegionOne %s public %s; " %(service['type'], service['http']) + \
                  "openstack endpoint create --region RegionOne %s internal %s; " %(service['type'], service['http']) + \
                  "openstack endpoint create --region RegionOne %s admin %s " %(service['type'], service['http'])
            exec_cmd(cmd)
        
    cmd = "openstack user create --domain default --password %s %s" % (passwd, user)
    exec_cmd(cmd)
    cmd = "openstack role add --project service --user %s admin" % user
    exec_cmd(cmd)
    __create_service(serviceopt[user])


def print_result():
    os.environ.update(admin_env)
    cmd = "openstack token issue ; " + \
          "openstack project list; " + \
          "openstack service list; " + \
          "openstack endpoint list "
    os.system(cmd)

def restart_service():
    cmd = "service glance-registry restart; " + \
          "service glance-api restart; " + \
          "service nova-api restart; " + \
          "service nova-consoleauth restart; " + \
          "service nova-scheduler restart; " + \
          "service nova-conductor restart; " + \
          "service nova-novncproxy restart; " + \
          "service nova-api restart; " + \
          "service neutron-server restart; " + \
          "service neutron-linuxbridge-agent restart; " + \
          "service neutron-dhcp-agent restart; " + \
          "service neutron-metadata-agent restart; " + \
          "service neutron-l3-agent restart; " + \
          "service cinder-scheduler restart; " + \
          "service cinder-api restart "
    exec_cmd(cmd)

def REST(name):
    if name == 'all':
        create_db(dbopt['keystone'])
        keystone_init()
        os.environ.update(admin_env)
        create_project_service()
        create_user_and_service('glance', GLANCE_PASS)
        create_user_and_service('nova', NOVA_PASS)
        create_user_and_service('neutron', NEUTRON_PASS)
        create_user_and_service('cinder', CINDER_PASS)

    os.environ.update(admin_env)
    if name == 'all' or name == 'glance':
        create_db(dbopt['glance'])
    if name == 'all' or name == 'nova':
        create_db(dbopt['nova'])
    if name == 'all' or name == 'neutron':
        create_db(dbopt['neutron'])
    if name == 'all' or name == 'cinder':
        create_db(dbopt['cinder'])


    restart_service()
    print_result()

REST('all')
