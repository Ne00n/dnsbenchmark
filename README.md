# README
This is DNS benchmarking tool.

## Features:
- Checking responsivenes of DNS resolver
- Checking stability of DNS resolver

## Todo:
- Rewrite to Python3 [ % ]
- Docker [ % ]


## Run:
```
python2 bot.py --dns 1.1.1.1 --hostnames domains.dat --threads 50
```
 

## Benchmarks - Not Cached:

### 1. Google Public DNS
```
DNS: 8.8.8.8
Hostnames: 1000000
Threads: 50
Runtime: 19.548058033 sec.
Total tested: 2254 [ 100 % ]
Good: 1924 [ 85.36 % ]
Failed: 330 [ 14.64 % ]
Avg speed: 0.189585383246
```
Comment: throttling is not huge. It can easily handle 50 req/s

### 2. Quad9 Public DNS
```
DNS: 9.9.9.9
Hostnames: 1000000
Threads: 50
Runtime: 22.1904921532 sec.
Total tested: 2153 [ 100 % ]
Good: 2143 [ 99.54 % ]
Failed: 10 [ 0.46 % ]
Avg speed: 0.270348230367
```
Comment: Almost no throtling. Very stable


### 3. Cloudflare Public DNS 
```
DNS: 1.1.1.1
Hostnames: 1000000
Threads: 50
Runtime: 18.3919110298 sec.
Total tested: 150 [ 100 % ]
Good: 9 [ 6.00 % ]
Failed: 141 [ 94.00 % ]
Avg speed: 0.429585642285
```

Comment: Throttling is huge. Not messurable at all. When they started service, this was way fastest, unthrottled DNS. For cached DNS requests






## Benchmarks - Cached:

### 1. Google Public DNS
```
DNS: 8.8.8.8
Hostnames: 9
Threads: 50
Runtime: 10.9113631248 sec.
Total tested: 1755 [ 100 % ]
Good: 1755 [ 100.00 % ]
Failed: 0 [ 0.00 % ]
Avg speed: 0.0981799129747 sec.
```
Comment: Very fast!

Command: ```python2 bot.py --dns 8.8.8.8 --hostnames domains_cached.dat --threads 50```

 

### 2. Quad9 Public DNS
```
DNS: 9.9.9.9
Hostnames: 9
Threads: 50
Runtime: 11.0902450085 sec.
Total tested: 2652 [ 100 % ]
Good: 2651 [ 99.96 % ]
Failed: 1 [ 0.04 % ]
Avg speed: 0.124706980688 sec.
```
Comment: Almost no throtling. Very stable

Command: ```python2 bot.py --dns 9.9.9.9 --hostnames domains.dat --threads 50```

### 3. Cloudflare Public DNS 
```
DNS: 1.1.1.1
Hostnames: 9
Threads: 50
Runtime: 18.3657209873 sec.
Total tested: 151 [ 100 % ]
Good: 14 [ 9.27 % ]
Failed: 137 [ 90.73 % ]
Avg speed: 0.0599012204579 sec.
```

Comment: Throttling is huge. 

Command: ```python2 bot.py --dns 1.1.1.1 --hostnames domains.dat --threads 50```

