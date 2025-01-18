#!/usr/bin/env python3

import socket 
import threading
import argparse
import textwrap

class ThreadScan:
    def __init__(self, scan_method):
        self.scan_method = scan_method

    def run_scan(self, args, target, port):
        first_port, last_port = self.args.port
        if first_port > last_port:
            print("Invalid port range.")
            return
        port_range = range(first_port, last_port + 1)
        # Initializes an empty list to keep track of thread objects
        threads = []
        for port in port_range:
            thread = threading.Thread(target=self.scan_method, args=(self.args, self.target, port))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

class TCPScan(ThreadScan):
    def __init__(self, args, target, port):
        #Invoking method from ThreadScan
        super().__init__(self.tcp_scan)
        self.args = args
        self.target = target
        self.port = port

    def tcp_scan(self, args, target, port):
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(1)
        try:
            answer = sock_tcp.connect_ex((target, port))
            if answer == 0:
                print(f"Port: {port} is open!")
            else:
                print(f"Port: {port} is closed!")
        except Exception as e:
            print(f'Error while scanning port {port}: {e}')
        finally:
            sock_tcp.close()
   
class UDPScan(ThreadScan):
    def __init__(self, args, target, port):
        super().__init__(self.udp_scan)
        self.args = args
        self.target = target
        self.port = port

    def udp_scan(self, args, target, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
            sock_udp.settimeout(1)
            try:
                sock_udp.sendto(b'www.google.com',(target, port))
                data, _ = sock_udp.recvfrom(1024)
                print(f"Port: {port} is open!")
            except socket.timeout:
                print(f"Port: {port} is open | filtered!")
            except socket.error as e:
                print(f"Port: {port} is closed or unreachable: {e}")   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'TCP and UDP port scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        epilog=textwrap.dedent('''Example:
        ./simple_scanner.py -t 192.168.0.1 -p 80 --tcp
        ./simple_scanner.py -t 192.168.0.1 -p 53 --udp 
        ./simple_scanner.py -t 192.168.0.1 -p 22 80 --tcp'''))
    parser.add_argument('-t', '--target', default='192.168.0.1', help='specified IP')
    parser.add_argument('-p', '--port', type=int, nargs='+', default=80, help='specified port')
    parser.add_argument('--tcp', action='store_true', help='Use TCP port for scanning')
    parser.add_argument('--udp', action='store_true', help='Use UDP port for scanning')
    args = parser.parse_args()
    
    if len(args.port) > 1:
        if args.tcp:
            tcp_scan = TCPScan(args, args.target, args.port)
            tcp_scan.run_scan(args, args.target, args.port)
        else:
            udp_scan = UDPScan(args, args.target, args.port)
            udp_scan.run_scan(args, args.target, args.port)
    else:
         if args.tcp:
             one = sum(args.port)
             args.port = one
             run = TCPScan(args, args.target, args.port)
             run.tcp_scan(args, args.target, args.port)
         else:
             one = sum(args.port)
             args.port = one
             run = UDPScan(args, args.target, args.port)
             run.udp_scan(args, args.target, args.port)
