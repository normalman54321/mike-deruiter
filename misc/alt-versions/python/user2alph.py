#!/usr/bin/python3

# user2alph
# Changes all usernames that have a number at the end to have letters at the 
# end, so that 1 ... 26 become _A ... _B, 27 ... 52 become AA ... AZ, etc.
#   ex: test01 -> test_A
#       test02 -> test_B
#       test27 -> testAA
#       test28 -> testAB

# NOTE: Only tested on Ubuntu systems

import os, sys, subprocess, pwd, re

# Function defintions ##########################################################

def show_usage(message, code=1):
    print(message)
    print("Usage: %s" % (sys.argv[0]))
    sys.exit(code)

def shell(command):
    proc = subprocess.Popen(command, shell=True)
    proc.wait()
    
    return proc.returncode

# Start of script ##############################################################

PROGNAME = os.path.split(sys.argv[0])[1]

if os.geteuid() != 0:
    show_usage("%s: must be run as root." % (PROGNAME))

passwd = open("/etc/passwd", "r")

names = []
re_num_at_end = re.compile(r'([^0-9]*)([0-9]+)$')

for line in passwd:
    fields = line.split(":")
    
    rematch_username = re_num_at_end.match(fields[0])
    
    if int(fields[2]) >= 1000 and rematch_username:
        names.append(fields[0])

for name in names:
    rematch_username = re_num_at_end.match(name)
    basename = rematch_username.group(1)
    num_at_end = int(rematch_username.group(2))
    
    alpha = []
    i = num_at_end
    
    while i > 0:
        alpha.append(chr(ord('A') + ((i - 1) % 26)))
        
        if i % 26 == 0:
            i -= 26
            
        i /= 26
   
    if num_at_end == 0:
        alpha.append('a')
        
    if num_at_end < 26:
        alpha.append('_')
        
    alpha.reverse()
    
    newname = basename + ''.join(alpha)
    
    try:
        # Check if new name already exists
        pwd.getpwnam(newname)
        print("%-8s : <error renaming user - already exists>" % (name))
    except KeyError:
        # It doesn't, so change directory, then change group (script assumes
        # users all have their own group named after them), then finally change
        # username
        if shell("usermod -d /home/%s -m %s" % (newname, name)) == 0:
            if shell("groupmod -n %s %s" % (newname, name)) == 0:
                shell("usermod -l %s %s" % (newname, name))
                print("%-8s : %s" % (name, newname))
            else:
                shell("usermod -d /home/%s -m %s" % (name, name))
                print("%-8s : <error renaming user - can't rename group>" % 
                      (name))
        else:
            print("%-8s : <error renaming user - can't rename home>" % (name))
