class MSG:
	master = None
	msg = None
	data = None
	def __init__(self,data,msg="", master = False ):
		self.master = master
		self.msg = msg
		self.data = data
	def view(self):
		print("\nMaster: ",self.master,"\nMessage: ",self.msg,"\nData: ",self.data)
	def getJson(self):
		return {'master':self.master,'msg':self.msg,'data':self.data}
	def loadJson(self,rawData):
		decodedData = rawData.decode('ASCII')
		obj = json.loads(decodedData)
		print("recieved obj ",obj,self)
		self.master = obj.master
		self.msg = obj.msg
		self.data = obj.data
	def dumpJson(self):
		rawData = json.dumps(self.getJson())
		return rawData.encode('ASCII')
a = MSG({})
a.view()
	