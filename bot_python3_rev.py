#!/usr/bin/python2
import os
import sys
import time
import copy
import random
import string
import socket
import struct

try:
    import _thread
except:
    import _thread as thread

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--dns', help='dns to test', required=True)
parser.add_argument('--hostnames', help='hostnames for testing', required=True)
parser.add_argument('--threads', help='max threads', default=30)
args = vars(parser.parse_args())


__DIR__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,__DIR__ + "/dependencies/")

import logger
import raw_dns
import threading_control


class dns_bench():

    def __init__(self, args):
        self.ts_start = time.time()

        self.loc_hostnames = args['hostnames']
        self.max_threads = int(args['threads'])
        self.dns = args['dns']

        self.hostnames = {}
        self.load_hostnames()
        self.mutex = _thread.allocate_lock()

        self.stats = {
            'total': 0,
            'good': 0,
            'failed': 0,
            'time': 0.0,
        }

    #
    # Load hostnames
    #
    def load_hostnames(self):
        logger.dump('load_hostnames(): %s' %(self.loc_hostnames), 'good')

        try:
            with open(self.loc_hostnames, 'r') as infile:
                for line in infile:
                    line = line.replace('\r', '')
                    line = line.replace('\n', '')
                    line = line.replace('\t', '')
                    
                    if line == '':
                        continue

                    self.hostnames[line] = ''
        except:
            logger.dump('load_hostnames(): %s' %(str(sys.exc_info())), 'critical')

        self.hostnames = list(self.hostnames.keys())
        self.hostnames = list(self.hostnames)




    #
    # Thread for checking if subdomain exist
    #
    def check(self, hostname, type_check):
        ts1 = 0
        ts2 = 0
        error = 0
        timeout = 1.1

        while error <= 2:
            t1 = time.time()
            res = raw_dns.query(hostname, self.dns, timeout, type_check)
            t2 = time.time()
            
            if res['status'] in [ 'timeout' ]:
                timeout = 2.5
                error += 1
            else:
                break

        # save results
        self.mutex.acquire()

        if res['status'] in [ 'timeout' ]:
            self.stats['failed'] += 1
            logger.dump("check | %s | %s" %(hostname, res), "info")
        else:
            self.stats['time'] += t2 - t1
            self.stats['good'] += 1

        self.stats['total'] += 1

        self.mutex.release()


        self.ref_tc.dec_threads()



    #
    # Percentage calculator
    #
    def perc(self, total, x):
        try:
            y = (100.0 * x) / total
        except:
            y = 0.0

        if y > 100.0:
            y = 100.0
        
        y = "%.2f" %(y)
        
        return y



    #
    # print stats
    #
    def print_stats(self):
        m = ""

        m += "DNS: %s\n" %(self.dns)
        total_hostnames = len(self.hostnames)
        m += "Hostnames: %d\n" %(total_hostnames)
        m += "Threads: %s\n" %(self.max_threads)
        
        runtime = time.time() - self.ts_start 
        m += "Runtime: %s sec.\n" %(runtime)
        m += "Total tested: %s [ %s ]\n" %(self.stats['total'], '100 %')

        perc_good = self.perc(self.stats['total'], self.stats['good'])
        m += "Good: %s [ %s ]\n" %(self.stats['good'], perc_good + ' %')

        perc_failed = self.perc(self.stats['total'], self.stats['failed'])
        m += "Failed: %s [ %s ]\n" %(self.stats['failed'], perc_failed + ' %')

        try:
            avg_speed = self.stats['time'] / self.stats['good']
        except:
            avg_speed = 0.0
        m += "Avg speed: %s sec.\n" %(avg_speed)

        logger.dump(m, "debug")



    #
    # Main method
    #
    def run(self):
        self.ts_start = time.time()
        self.ref_tc = threading_control.threading_control(max_work=3600, max_threads=self.max_threads)

        it = 0
        while 1:
            it += 1
            self.ref_tc.wait_threads()
            self.ref_tc.inc_threads()

            if it % 2 == 0:
                hostname = random.choice(self.hostnames)
                _thread.start_new_thread(self.check, (hostname, 'a'))
            else:
                random_ip = random.randint(1, 0xffffffff)
                random_ip = socket.inet_ntoa(struct.pack('>I', random_ip))
                _thread.start_new_thread(self.check, (random_ip, 'ptr'))

            if it % 100 == 0:
                self.print_stats()

            if self.ref_tc.can_work() == False:
                break

        while self.ref_tc.get_total_threads() > 0 and self.ref_tc.can_work() == True:
            time.sleep(0.3)



if __name__ == '__main__':
    d = dns_bench(args)
    d.run()
