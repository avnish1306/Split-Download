
def getFileDetails(OWNIP,distributionMsg,socket,flag=True):
	laddr= socket.getsockname()[0]
	raddr = socket.getpeername()[0]
	if True:
		addr = laddr if laddr!=OWNIP else raddr
	else:
		addr = laddr if laddr==OWNIP else raddr
	segment = distributionMsg.data["clientIpSegmentMap"][addr].split("-")
	fileSize = int(segment[1])-int(segment[0])+1
	filenameWithExt = distributionMsg.data['filenameWithExt']
	fileName = filenameWithExt.split('.')[0] + str(distributionMsg.data["clientIpSegmentMap"][addr])+".spld"
	return (fileName,fileSize)
	