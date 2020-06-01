
def getFileDetails(OWNIP,distributionMsg,socket):
	laddr= socket.getsockname()[0]
	raddr = socket.getpeername()[0]
	addr = laddr if laddr!=OWNIP else raddr
	segment = distributionMsg.data["clientIpSegmentMap"][addr].split("-")
	fileLink = distributionMsg.data["fileLink"]
	fileSize = int(segment[1])-int(segment[0])+1
	url = fileLink.split('/')
	fileName = str(url[len(url) - 1]) + str(distributionMsg.data["clientIpSegmentMap"][addr])
	return (fileName,fileSize)
	