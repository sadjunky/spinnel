# Spinnel

A miniature distributed file system, developed in an attempt to explore and understand the core principles behind the HDFS architecture. It consists of one master and multiple slaves, and a client for interacting with the master node. On signaling the master node with `SIGINT`, it will dump the metadata/namespace and reload it when lauched the next time. Just how HDFS achieves data replication across slaves through TCP, Spinnel will send data to one slave and the slave will send the data to next and so on, producing a cascading effect. Similarly, reads are achieved by reading from one slave, if failed, it will attempt to read from the next slave and so on. [RPyC](https://rpyc.readthedocs.io/en/latest/#) has been used for implementing RPCs.

## Requirements
- RPyC

## Get started
1. Edit the `spinnel.conf` for setting block size, the replication factor and slave list.
2. Launch the master and the slaves.
3. To store and retrieve a file:
```sh
$ python client.py put punkrockrulez.txt the_clash
$ python client.py get the_clash
```
4. Quit using Ctrl + C so that it dumps the namespace.

## TODO
1. Implement deletion
2. Implement a more efficient algorithm for slave selection to store a block (currently the selection is random)
3. Implement slave heartbeats
4. Addition of entry in namespace only after data write succeeds
5. Implement master failover and election (probably using Zookeeper as failure detector and master elector)
6. Implement a proper data structure (a tree data structure like [treedict](https://github.com/hoytak/treedict)) to store namespace data (currently uses `simpledict`)
7. Write a FUSE (Filesystem in Userspace) adapter to mount Spinnel as a locally available UNIX filesystem
8. Write a CLI for better interface experience
