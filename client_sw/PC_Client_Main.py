from AdamModule import adam

try:
	iomodule = adam.adam6000("192.168.50.15")
	succes = iomodule.connect()
	iomodule.writepoutputport(0,True)
	stat = iomodule.readinputno(0)

		

except Exception, errormsg:
    print "\n"
    print "Error message: %s" % errormsg
    raw_input("Press key to exit.")
    sys.exit(-1)

print("End")