import requests

payload = {
        "post": "Today is a great day!",
        "platforms": ["linkedin"],
	"mediaUrls": ["https://img.ayrshare.com/012/gb.jpg"],
      }
      
# Live API Key
headers = {'Content-Type': 'application/json', 
              'Authorization': 'Bearer C17DG4B-F2P41GW-QKJ56NV-KHQRM5T'}
      
r = requests.post('https://app.ayrshare.com/api/post', 
          json=payload, 
          headers=headers)
print(r)