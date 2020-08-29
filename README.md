# Network-Troubleshooting-Framework-using-MINT-and-P4-in-SDN

The network troubleshooting framework using MINT is a framework that allows the collection of network state information from the data plane without the involvement of control plane using MINT and analysing the collected data to identify a network problem/anomaly or in other words troubleshooting the network issues.

## Topology
![](/topology.jpg)

## Setup
1. P4.org have created a VM with everything needed to work on their P4 tutorial exercises or to build up your own, including the P4 Compiler, Behavioral Model, starter code, and editors. Thus the first step is to download the VM. For downoading the VM refer to Virtual Machine section under Beginner's Track [https://p4.org/events/2019-04-30-p4-developer-day/]
2. After downloading the VM, use any free and open source hypervisor like VirtualBox for importing and running the VM.
3. After installing the VM, in the P4 folder checkout the repository under the exercises folder.

## Run
For running the framework execute the following commands in order:
1. Stop any existing processes
```
    make stop
````
2. Cleanup any logs or pcap files  
```
    make clean
```

3. Start the framework   
```
    make run
```

4. In a separate terminal, start the controller and type 1 in the terminal to switch on the MINT process.  
```
    python controller.py
```

5. Also, start the data collector application i.e. **collector.py** and data debugger application i.e. **debug.py** in separate terminals.
 ```
     python collector.py
     python debug.py
 ```

6. In the mininet terminal start the xterms for h1 (host), h2 (host), live server (h3) and static server(h4)  
```
    xterm h1 h2 h3 h4
```

7. In the xterm terminals for live server and static server, execute the terminator.py program for start receiving any incoming packets and sending the extracted data to data collector application.
```
    python treminate.py
```

8. In the xterm terminals for host h1 and/or h2 execute the send.py prgram by specifying the *destination IP* and *message* to send the packets to live server or static server
```
    python send.py "10.0.4.4" "Sending message to static server"
    python send.py "10.0.3.3" "Sending message to live server"
```

9. Interact with the debug.py application to query required network statistics like queuing delay, packet route, total switching delay etc.

## System Requirements
1. Operating system - Any OS like Windows, Ubuntu
2. A hypervisor like virtual box for running the VM.
3. Disk space of atleast 8-10 GB
4. Ram - atleast 4 GB
