import sys
import subprocess

p1 = subprocess.Popen(
    ['python', 'lib/pychess/Players/PyChess.py'],
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE)

p2 = subprocess.Popen(
    ['python', 'lib/pychess/Players/PyChess.py'],
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE)

# process-in
def pin(proc, msg):
	proc.stdin.write(msg + '\n')

def pout(proc):
	return proc.stdout.readline()

def println(msg):
	sys.stdout.write(msg)

def getBoard(proc):
	pin(proc, 'moves')
	for i in range(11):
		println(pout(proc))

# Set time constraints
pin(p1, 'level 0 3 0')
pin(p2, 'level 0 3 0')

# tell player 1 to start
pin(p1, 'go')
pout(p1)
move = pout(p1)
getBoard(p1)
# hit enter
cmd = sys.stdin.readline()
pin(p2, move)
pout(p2)
response = pout(p2)
getBoard(p2)
# hit enter
cmd = sys.stdin.readline()

# loop
while True:
	pin(p1, response)
	pout(p1)
	move = pout(p1)
	getBoard(p1)
	# hit enter
	cmd = sys.stdin.readline()
	pin(p2, move)
	pout(p2)
	response = pout(p2)
	getBoard(p2)
	# hit enter
	cmd = sys.stdin.readline()


proc.stdin.close()
proc.wait()