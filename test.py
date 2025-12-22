from requests import *
  

data = {
    "username": "bebra",
    "password": "123456",
    "rightsLevel": 1
}
r = post("http://127.0.0.1:5000/newUser", json=data)

print(r.status_code)
