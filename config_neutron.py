import utils
import os
import deploy

RABBIT_PASS= '123456'
METADATA_SECRET = '123456'
PROVIDER_INTERFACE_NAME = 'eth0'

config_2_neutron = \
    {
     "filename":"/etc/neutron/neutron.conf",
     "database":{
        "connection": "mysql+pymysql://neutron:%s@%s/neutron" %(deploy.NEUTRON_DBPASS, deploy.CONTROLLER_HOSTNAME)
        },
     "DEFAULT":{
        "transport_url": "rabbit://openstack:%s@%s" % (RABBIT_PASS, deploy.CONTROLLER_HOSTNAME),
        "auth_strategy": "keystone",
        "core_plugin": "ml2",
        "service_plugins": "",
        "allow_overlapping_ips":"false",
        "notify_nova_on_port_status_changes": "True",
        "notify_nova_on_port_data_changes": "True"
        },
     "keystone_authtoken":{
        "auth_uri": "http://%s:5000" % deploy.CONTROLLER_HOSTNAME,
        "auth_url": "http://%s:35357" % deploy.CONTROLLER_HOSTNAME,
        "memcached_servers": "%s:11211" % deploy.CONTROLLER_HOSTNAME,
        "auth_type": "password",
        "project_domain_name": "Default",
        "user_domain_name": "Default",
        "project_name": "service",
        "username": "neutron",
        "password": deploy.NEUTRON_PASS
        },
     "nova":{
        "auth_url": "http://%s:35357" % deploy.CONTROLLER_HOSTNAME,
        "auth_type": "password",
        "project_domain_name": "Default",
        "user_domain_name": "Default",
        "region_name": "RegionOne",
        "project_name": "service",
        "username": "nova",
        "password": deploy.NOVA_PASS
        }
     }

config_3_neutron = \
    {
     "filename":"/etc/neutron/neutron.conf",
     "database":{
        "connection": "mysql+pymysql://neutron:%s@%s/neutron" %(deploy.NEUTRON_DBPASS, deploy.CONTROLLER_HOSTNAME)
        },
     "DEFAULT":{
        "transport_url": "rabbit://openstack:%s@%s" % (RABBIT_PASS, deploy.CONTROLLER_HOSTNAME),
        "auth_strategy": "keystone",
        "core_plugin": "ml2",
        "service_plugins": "router",
        "allow_overlapping_ips":"true",
        "notify_nova_on_port_status_changes": "True",
        "notify_nova_on_port_data_changes": "True"
        },
     "keystone_authtoken":{
        "auth_uri": "http://%s:5000" % deploy.CONTROLLER_HOSTNAME,
        "auth_url": "http://%s:35357" % deploy.CONTROLLER_HOSTNAME,
        "memcached_servers": "%s:11211" % deploy.CONTROLLER_HOSTNAME,
        "auth_type": "password",
        "project_domain_name": "Default",
        "user_domain_name": "Default",
        "project_name": "service",
        "username": "neutron",
        "password": deploy.NEUTRON_PASS
        },
     "nova":{
        "auth_url": "http://%s:35357" % deploy.CONTROLLER_HOSTNAME,
        "auth_type": "password",
        "project_domain_name": "Default",
        "user_domain_name": "Default",
        "region_name": "RegionOne",
        "project_name": "service",
        "username": "nova",
        "password": deploy.NOVA_PASS
        }
     }

config_2_ml2_conf = \
    {
     "filename":"/etc/neutron/plugins/ml2/ml2_conf.ini",
     "ml2": {
        "type_drivers": "flat,vlan",
        "tenant_network_types": "",
        "mechanism_drivers": "linuxbridge",
        "extension_drivers": "port_security"
        },
     "ml2_type_flat":{
        "flat_networks": "provider"
        },
     "ml2_type_vxlan":{
        "vni_ranges": ""
        },
     "securitygroup":{
        "enable_ipset": "True"
        }
     }

config_3_ml2_conf = \
    {
     "filename":"/etc/neutron/plugins/ml2/ml2_conf.ini",
     "ml2":{
        "type_drivers": "flat,vlan,vxlan",
        "tenant_network_types": "vxlan",
        "mechanism_drivers": "linuxbridge,l2population",
        "extension_drivers": "port_security"
        },
     "ml2_type_flat":{
        "flat_networks": "provider"
        },
     "ml2_type_vxlan":{
        "vni_ranges": "1:1000"
        },
     "securitygroup":{
        "enable_ipset": "True"
        }
     }

config_2_linuxbridge_agent = \
    {
     "filename":"/etc/neutron/plugins/ml2/linuxbridge_agent.ini",
     "linux_bridge":{
        "physical_interface_mappings": "provider:%s" % PROVIDER_INTERFACE_NAME
        },
     "vxlan":{
        "enable_vxlan": "False",
        "local_ip": "<None>",
        "l2_population": "False",
        },
     "securitygroup":{
        "enable_security_group": "True",
        "firewall_driver": "neutron.agent.linux.iptables_firewall." +
                           "IptablesFirewallDriver"
        }
     }

config_3_linuxbridge_agent = \
    {
     "filename":"/etc/neutron/plugins/ml2/linuxbridge_agent.ini",
     "linux_bridge":{
        "physical_interface_mappings": "provider:%s" % PROVIDER_INTERFACE_NAME
        },
     "vxlan":{
        "enable_vxlan": "True",
        "local_ip": "",
        "l2_population": "True",
        },
     "securitygroup":{
        "enable_security_group": "True",
        "firewall_driver": "neutron.agent.linux.iptables_firewall." +
                           "IptablesFirewallDriver"
        }
     }

config_23_dhcp_agent = \
    {
     "filename":"/etc/neutron/dhcp_agent.ini",
     "DEFAULT":{
        "interface_driver": "neutron.agent.linux.interface." +
                            "BridgeInterfaceDriver",
        "dhcp_driver": "neutron.agent.linux.dhcp.Dnsmasq",
        "enable_isolated_metadata": "True"
        }
    }

config_23_metadata_agent = \
    {
     "filename":"/etc/neutron/metadata_agent.ini",
     "DEFAULT":{
        "nova_metadata_ip": deploy.CONTROLLER_HOSTNAME,
        "metadata_proxy_shared_secret": METADATA_SECRET
        }
    }

config_3_l3_agent = \
    {
     "filename":"/etc/neutron/l3_agent.ini",
     "DEFAULT":{
        "interface_driver": "neutron.agent.linux.interface.BridgeInterfaceDriver"
        },
    }

configs_2 = [config_2_neutron, config_2_ml2_conf, config_2_linuxbridge_agent, config_23_dhcp_agent, config_23_metadata_agent]
configs_3 = [config_3_neutron, config_3_ml2_conf, config_3_linuxbridge_agent, config_23_dhcp_agent, config_23_metadata_agent, config_3_l3_agent]

def do_config(configs):
    for cfg in configs:
        parser = utils.Config(cfg['filename'])
        del cfg['filename']
        parser.set(cfg)
        parser.write()

