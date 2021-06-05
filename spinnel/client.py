import os
import sys

import rpyc

def send_to_slave(block_uuid, data, slaves):
    print("sending: " + str(block_uuid) + str(slaves))
    slave=slaves[0]
    slaves=slaves[1:]
    host, port=slave.split(":")

    con=rpyc.connect(host, port=port)
    slave = con.root.Slave()
    slave.put(block_uuid, data, slaves)


def read_from_slave(block_uuid, slave):
   host, port = slave.split(":")
   con=rpyc.connect(host, port=port)
   slave = con.root.Slave()
   return slave.get(block_uuid)


def get(master, fname):
    file_table = master.get_file_table_entry(fname)
    if not file_table:
        print("404: file not found")
        return
    for block in file_table:
        for m in [master.get_slaves()[_] for _ in block[1]]:
            data = read_from_slave(block[0], m)
            if data:
                sys.stdout.write(data)
                break
        else:
            print("No blocks have been found. Likely a corrupt file")


def put(master, source, dest):
    size = os.path.getsize(source)
    blocks = master.write(dest, size)
    with open(source) as f:
        for b in blocks:
            data = f.read(master.get_block_size())
            block_uuid=b[0]
            slaves = [master.get_slaves()[_] for _ in b[1]]
            send_to_slave(block_uuid, data, slaves)


def main(args):
    con=rpyc.connect("localhost", port=2131)
    master=con.root.Master()

    if args[0] == "get":
        get(master, args[1])
    elif args[0] == "put":
        put(master, args[1], args[2])
    else:
        print("Please enter 'put srcFile destFile OR get file'")


if __name__ == "__main__":
    main(sys.argv[1:])
