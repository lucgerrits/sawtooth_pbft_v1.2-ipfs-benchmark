import requests
import json

org_url="10.1.0.222"
new_url="127.0.0.1:8080"
i=0
i2=0
i3=0
f = open("tmp.txt", "r")
for line in f:
	response = requests.get(line.replace(org_url, new_url).strip())
	response = json.loads(response.text)
	if response["data"][0]["status"] == "COMMITTED":
		i+=1
	elif response["data"][0]["status"] == "PENDING":
		i2+=1
	else:
		i3+=1
		print(response)
print("comitted", i)
print("pending", i2)
print("error",i3)
print("total",i+i2+i3)
