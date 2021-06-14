import configparser
import math
import os
import pickle
import random
import signal
import sys
import uuid

import rpyc

from rpyc.utils.server import ThreadedServer

def int_handler(signal, frame):
   pickle.dump((MasterService.ExposedMaster.file_table,MasterService.ExposedMaster.block_mapping), open('fs.img', 'wb'))
   sys.exit(0)

def set_conf():
    conf=configparser.ConfigParser()
    conf.readfp(open('spinnel.conf'))
    
    MasterService.ExposedMaster.block_size = int(conf.get('master', 'block_size'))
    MasterService.ExposedMaster.replication_factor = int(conf.get('master', 'replication_factor'))
    
    slaves = conf.get('master', 'slaves').split(',')
    for m in slaves:
        id, host, port=m.split(":")
        MasterService.ExposedMaster.slaves[id]=(host, port)
    
    if os.path.isfile('fs.img'):
        MasterService.ExposedMaster.file_table,MasterService.ExposedMaster.block_mapping = pickle.load(open('fs.img', 'rb'))

class MasterService(rpyc.Service):
    class ExposedMaster():
        file_table = {}
        block_mapping = {}
        slaves = {}

        block_size = 0
        replication_factor = 0

        def exposed_read(self, fname):
            mapping = self.__class__.file_table[fname]
            return mapping

        def exposed_write(self, dest, size):
            if self.exists(dest):
                pass # ignoring for now, will remove later  

            self.__class__.file_table[dest]=[]

            num_blocks = self.calc_num_blocks(size)
            blocks = self.alloc_blocks(dest, num_blocks)
            return blocks   

        def exposed_put(self, val):
            self.__class__.replication_factor = val
        
        def exposed_get_file_table_entry(self, fname):
            if fname in self.__class__.file_table:
                return self.__class__.file_table[fname]
            else:
                return None

        def exposed_get_block_size(self):
            return self.__class__.block_size

        def exposed_get_slaves(self):
            return self.__class__.slaves

        def calc_num_blocks(self, size):
            return int(math.ceil(float(size)/self.__class__.block_size))

        def exists(self, file):
            return file in self.__class__.file_table

        def alloc_blocks(self, dest, num):
            blocks = []
            for i in range(0,num):
                block_uuid = uuid.uuid1()
                nodes_ids = random.sample(self.__class__.slaves.keys(), self.__class__.replication_factor)
                blocks.append((block_uuid, nodes_ids))

                self.__class__.file_table[dest].append((block_uuid,nodes_ids))

            return blocks


if __name__ == "__main__":
    set_conf()
    signal.signal(signal.SIGINT,int_handler)
    t = ThreadedServer(MasterService, port = 2131)
    t.start()
