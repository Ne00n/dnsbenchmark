#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import struct
import random



def domain_to_byte(domain):
    domain_to_byte = ''
    dsplit = domain.split('.')

    for cs in dsplit:
        formatstr = "B%ds" % len(cs)
        newsplit = struct.pack(formatstr, len(cs), cs)
        domain_to_byte += newsplit

    domain_to_byte += '\0'
    return domain_to_byte

def byte_to_domain(str):
    domain = ''
    i = 0
    length = struct.unpack('!B', str[0:1])[0]
    
    while length != 0 :
        i += 1
        domain += str[i:i+length]
        i += length
        length = struct.unpack('!B', str[i:i+1])[0]
        if length != 0 :
            domain += '.'
    
    return domain


def get_full_name(offset, Buf):
    full_record = ''
    one_char = struct.unpack('!B', Buf[offset:offset+1])[0]

    if one_char & 0xc0 == 0xc0 : 
        jump = struct.unpack('!h', Buf[offset:offset+2])[0]
        jump = jump & 0x3FFF 
        full_record += get_full_name(jump, Buf)
    elif one_char == 0 :
        return '\x00'
    else :
        full_record += Buf[offset:offset+one_char+1]
        full_record += get_full_name(offset+one_char+1, Buf)
        
    return full_record


def query(domain, dns_host='8.8.8.8', socket_timeout=1.0, search_for='a'):
    try:
        DHOST = dns_host
        DPORT = 53
        TIMEOUT = socket_timeout

        TID = random.randint(-32768, 32767)
        Flags = 0x0100
        Questions = 0x0001
        answer_rrs = 0x0000
        AuthorityRRs = 0x0000
        AdditionalRRs = 0x0000
        TIDCHARS = struct.pack('!h', TID)

        if search_for == 'ptr':
            domain = domain.split('.')
            domain.reverse()
            domain = '.'.join(domain)
            domain = domain + '.in-addr.arpa'



        domain = domain.encode('utf8', 'ignore')
        domainbyte = domain_to_byte(domain)
        #TYPE            value and meaning
        #A               1 a host address
        #NS              2 an authoritative name server
        #MD              3 a mail destination (Obsolete - use MX)
        #MF              4 a mail forwarder (Obsolete - use MX)
        #CNAME           5 the canonical name for an alias
        
        # 0001  A
        # 0002  NS
        # 0005  CNAME
        # 0006  SOA
        # 000c  PTR
        # 000f  MX
        # 0010  TXT
        # 001c  AAAA
        # 0026  A6
        # 00fb  IXFR
        # 00fc  AXFR
        # 00ff  wildcard



        if search_for == 'a':
            SEARCHTYPE = 0x0001
        
        if search_for == 'cname':
            SEARCHTYPE = 0x0005

        if search_for == 'mx':
            SEARCHTYPE = 0x000f

        if search_for == 'ptr':
            SEARCHTYPE = 0x000c



        #Class 一 1 Internet
        SEARCHCLASS = 0x0001

        bufhead = struct.pack('!hhhhhh', TID, Flags, Questions, answer_rrs, AuthorityRRs, AdditionalRRs)
        buftail = struct.pack('!hh', SEARCHTYPE, SEARCHCLASS)
        Buf = bufhead + domainbyte + buftail
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(TIMEOUT) # timeout
        
        s.sendto(Buf,(DHOST, DPORT))
        
        try:
            data, addr = s.recvfrom(1024)
        except socket.timeout:
            s.close()

            return {
                'status': 'timeout',
                'is_domain_valid': False,
                'results': [
                    False
                ]
            }
            
        s.close()
        results = {}


        # domain is valid
        is_domain_valid = False
        if data[2:4] == '\x81\x80':
            is_domain_valid = True

        # domain is not valid
        if data[2:4] == '\x81\x83':
            is_domain_valid = False

        # servfail
        if data[2:4] == '\x81\x82':
            return {
                'status': 'ok',
                'is_domain_valid': False,
                'results': []
            }


        if data[0:2] == TIDCHARS:
            # Header 
            # [0:2] TID
            # [2:4] Flags 
            # Flags 0000
            flags = struct.unpack('!h', data[2:4])[0]
            errormsg = flags & 0x000F
            if errormsg != 0:

                return {
                    'status': 'non_existing',
                    'is_domain_valid': False,
                    'results': [
                        False
                    ]
                }

            # [4:6]Questions
            # [6:8]Answer RRs
            # [8:10]Authority RRs
            # [10:12]Additional RRs
            answer_rrs = struct.unpack('!h', data[6:8])[0]
            bitflags = 12;
            
            # Question
            # Name: '\0'
            # Type: 
            # Class: 一 1(Internet)
            
            while data[bitflags] != '\x00':
                bitflags += 1
            bitflags += 1 # name
            bitflags += 2 # Type
            bitflags += 2 # Class
        
            i = 0

            while i < answer_rrs:
                # Name 
                bitflags += 2
                
                if data[bitflags:bitflags+2] == '\x00\x05' and search_for == 'cname': # CNAME
                    bitflags += 8
                    rdatalength = struct.unpack('!h', data[bitflags:bitflags+2])[0]
                    bitflags += 2
                    full_record = get_full_name(bitflags, data)
                    bitflags += rdatalength
                    cname = byte_to_domain(full_record)
                    results[cname] = ''
                
                elif data[bitflags:bitflags+2] == '\x00\x0c' and search_for == 'ptr': # PTR
                    bitflags += 8
                    rdatalength = struct.unpack('!h', data[bitflags:bitflags+2])[0]
                    bitflags += 2
                    full_record = get_full_name(bitflags, data)
                    bitflags += rdatalength
                    domain = byte_to_domain(full_record)
                    results[domain] = ''

                elif data[bitflags:bitflags+2] == '\x00\x01' and search_for == 'a': # A(Host Address)

                    if data[bitflags:bitflags+4] == '\x00\x01\x00\x00':

                        cname = query(domain, dns_host, socket_timeout, 'cname')
                        if len(cname['results']) > 0:
                            
                            if cname['results'][0] == False:
                                return {
                                    'status': 'non_existing',
                                    'is_domain_valid': False,
                                    'results': [
                                        False
                                    ]
                                }
                            else:
                                return query(cname['results'][0], dns_host, socket_timeout, 'a')
                        else:
                            return {
                                'status': 'ok',
                                'is_domain_valid': is_domain_valid,
                                'results': [
                                    False
                                ]
                            }
                    else:
                        try:
                            bitflags += 8
                            rdatalength = struct.unpack('!h', data[bitflags:bitflags+2])[0]
        
                            bitflags += 2
                            iptuple = struct.unpack('!BBBB', data[bitflags:bitflags+4])

                            ipstr = '%d.%d.%d.%d' % iptuple
                            bitflags += rdatalength
                            results[ipstr] = ''
                        except:
                            pass

                elif data[bitflags:bitflags+2] == '\x00\x0f' and search_for == 'mx': # MX
                    
                    while data[bitflags:bitflags+1] != '':
                        try:
                            bitflags += 8
                            rdatalength = struct.unpack('!h', data[bitflags:bitflags + 2])[0]
                            bitflags += 4
                            full_record = get_full_name(bitflags, data)
                            bitflags += rdatalength
                            mx = byte_to_domain(full_record)
                            mx = mx.strip()
                            if mx not in ['', False, None]:
                                results[mx] = ''
                        except:
                            pass
                i += 1

        return {
            'status': 'ok',
            'is_domain_valid': is_domain_valid,
            'results': results.keys(),
        }
    except:
        print("dns.Query('%s', '%s', %s): %s" %(domain, dns_host, socket_timeout, str(sys.exc_info())))


        return {
            'status': 'timeout',
            'is_domain_valid': False,
            'results': [
                False,
            ]
        }



if __name__ == '__main__':
    tests = [
        'ptr',
        'a',
        'cname',
        'mx'
    ]

    domain = sys.argv[1]

    for test in tests:
        res = query(domain, '8.8.8.8', 1.1, test)
        print(res)
