import socket
from AdamModule import adam




try:
	iomodule = adam.adam6000("192.168.1.1")
	succes = iomodule.connect()
	if succes:
		print("ss")
	else:
		print(" ! ERROR: Could not load Tool Environment, tool not started")

except Exception, errormsg:
    print "\n"
    print "Error message: %s" % errormsg
    raw_input("Press key to exit.")
    sys.exit(-1)

print("End")