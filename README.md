# Network-Troubleshooting-Framework-using-MINT-and-P4-in-SDN

The network troubleshooting framework using MINT is a framework that allows the collection of network state information from the data plane using MINT and analysing the collected data to identify the root cause of a network problem/anomaly or in other words troubleshooting the network issues.

# Topology
[The topology file considered for the framework](./topology.jpg?raw=true "Title")

# Setup
1. Setup the P4 virtual machine. P4.org have created a VM with everything needed to work on the P4 tutorial exercises, including the P4 Compiler, Behavioral Model, starter code, and editors. Download and run the VM. For downoading the VM refer to Virtual Machine section under Beginner's Track [https://p4.org/events/2019-04-30-p4-developer-day/]
2. On the VM in the P4 folder checkout the repository under the exercises folder.

# Run
For executing the framework execute the following commands in order:
1. make clean
2. make run
3. In the mininet terminal start the xterms 
