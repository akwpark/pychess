import sys
import subprocess

player = sys.argv[1]

# Create an instance of the modified PyChess engine
proc = subprocess.Popen(
    ['python', 'lib/pychess/Players/PyChess.py'],
    stdout=subprocess.PIPE,
    stdin=subprocess.PIPE)

# process-in
def pin(msg):
	proc.stdin.write(msg + '\n')

def pout():
	return proc.stdout.readline()

def println(msg):
	sys.stdout.write(msg)


pin('level 0 3 0')

if player == 'white':
	pin('go')
	# The declaration of wait time
	pout()
	# The actual move
	println(pout())

cmd = sys.stdin.readline()
while cmd != '':
	pin(cmd)
	# The declaration of wait time
	pout()
	# The actual move
	println(pout())

	# Get next input
	cmd = sys.stdin.readline()


proc.stdin.close()
proc.wait()