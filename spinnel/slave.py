import os
import uuid

import rpyc

from rpyc.utils.server import ThreadedServer

DATA_DIR="/tmp/slave/"


class SlaveService(rpyc.Service):
    class ExposedSlave():
        blocks = {}

        def exposed_put(self, block_uuid, data, slaves):
            with open(DATA_DIR+str(block_uuid),'w') as f:
                f.write(data)
            if len(slaves)>0:
                self.forward(block_uuid, data, slaves)

        def exposed_get(self, block_uuid):
            block_addr=DATA_DIR+str(block_uuid)
            if not os.path.isfile(block_addr):
                return None
            with open(block_addr) as f:
                return f.read()    

        def forward(self, block_uuid, data, slaves):
            print("8888: forwaring to:")
            print(block_uuid, slaves)
            slave=slaves[0]
            slaves=slaves[1:]
            host,port=slave.split(":")

            con=rpyc.connect(host, port=port)
            slave = con.root.slave()
            slave.put(block_uuid, data, slaves)
        
        def delete_block(self,uuid):
            pass

if __name__ == "__main__":
    t = ThreadedServer(SlaveService, port = 8888)
    #tt = ThreadedServer(SlaveService, port = 9999)
    t.start()
    #tt.start()
