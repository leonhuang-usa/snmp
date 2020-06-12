import sys
from pysnmp import hlapi
from pysnmp.hlapi import nextCmd, SnmpEngine, CommunityData, UdpTransportTarget,ContextData,ObjectType,ObjectIdentity

import time
from timeloop import Timeloop
from datetime import timedelta

def append_new_line(file_name, text_to_append):
#"""Append given text as a new line at the end of file"""
# Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)


def walk2log(host, oid, file_name):
    for (errorIndication,errorStatus,errorIndex,varBinds) in nextCmd(SnmpEngine(), 
        CommunityData('public'), UdpTransportTarget((host, 161)), ContextData(), 
        ObjectType(ObjectIdentity(oid)),lexicographicMode=False):
        if errorIndication:
            print(errorIndication, sys.stderr) #file=
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 
                                sys.stderr)    #file=         
            break
        else:
            for varBind in varBinds:
                #print(format(time.ctime()),varBind)
                tuple=(str(format(time.ctime())),str(varBind))
                append_new_line(file_name, ','.join(tuple))
                


def walk(host, oid):
    for (errorIndication,errorStatus,errorIndex,varBinds) in nextCmd(SnmpEngine(), 
        CommunityData('public'), UdpTransportTarget((host, 161)), ContextData(), 
        ObjectType(ObjectIdentity(oid)),lexicographicMode=False):
        if errorIndication:
            print(errorIndication, sys.stderr) #file=
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 
                                sys.stderr)    #file=         
            break
        else:
            for varBind in varBinds:
                print(varBind)
                
def construct_value_pairs(list_of_pairs):
    pairs = []
    for key, value in list_of_pairs.items():
        pairs.append(hlapi.ObjectType(hlapi.ObjectIdentity(key), value))
    return pairs

def fetch(handler, count):
        result = []
        for i in range(count):
            try:
                error_indication, error_status, error_index, var_binds = next(handler)
                if not error_indication and not error_status:
                    items = {}
                    for var_bind in var_binds:
                        items[str(var_bind[0])] = cast(var_bind[1])
                    result.append(items)
                else:
                    raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
            except StopIteration:
                break
        return result

def set(target, value_pairs, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        handler = hlapi.setCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            *construct_value_pairs(value_pairs)
        )
        return fetch(handler, 1)[0]

def construct_object_types(list_of_oids):
        object_types = []
        for oid in list_of_oids:
            object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
        return object_types

def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]

def cast(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    return str(value)
                except (ValueError, TypeError):
                    pass
        return value

def get_bulk(target, oids, credentials, count, start_from=0, port=161,
                 engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        handler = hlapi.bulkCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            start_from, count,
            *construct_object_types(oids)
        )
        return fetch(handler, count)

def get_bulk_auto(target, oids, credentials, count_oid, start_from=0, port=161,
                      engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        count = get(target, [count_oid], credentials, port, engine, context)[count_oid]
        return get_bulk(target, oids, credentials, count, start_from, port, engine, context)

#print(get('192.168.43.201', ['1.3.6.1.2.1.1.5.0'], hlapi.CommunityData('public')))

#its = get_bulk_auto('192.168.43.201', ['1.3.6.1.2.1.2.2.1.2 ', '1.3.6.1.2.1.31.1.1.1.18'], hlapi.CommunityData('public'), '1.3.6.1.2.1.2.1.0')
#
#for it in its:
#        for k, v in it.items():
#            print("{0}={1}".format(k, v))
#        print('')



#walk('192.168.43.201','1.3.6.1.2.1.2')

#walk('192.168.10.200', '1.3.6.1.2.1.2')
        
tl = Timeloop()

#@tl.job(interval=timedelta(seconds=2))
#def sample_job_every_2s():
#    print ("2s job current time : {}".format(time.ctime()))
#    
#@tl.job(interval=timedelta(seconds=5))
#def sample_job_every_5s():
#    print ("5s job current time : {}".format(time.ctime()))
    
@tl.job(interval=timedelta(seconds=30))
def sample_job_1_10s():
    #print ("10s job current time : {}".format(time.ctime()))
    #walk2log('192.168.43.201','1.3.6.1.2.1.2','1.log')
    walk2log('192.168.10.200', '1.3.6.1.2.1.2','GantrySW.log')



@tl.job(interval=timedelta(seconds=30))
def sample_job_2_10s():
    #print ("10s job current time : {}".format(time.ctime()))
    #walk('192.168.43.201','1.3.6.1.2.1.2')
    walk2log('192.168.10.200', '1.3.6.1.2.1.2','StandSW.log')

@tl.job(interval=timedelta(seconds=30))
def sample_job_3_10s():
    #print ("10s job current time : {}".format(time.ctime()))
    #walk('192.168.43.201','1.3.6.1.2.1.2')
    walk2log('192.168.10.200', '1.3.6.1.2.1.2','OpConSW.log')
#    
if __name__ == "__main__":
    tl.start(block=True)

