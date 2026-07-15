import requests



BASE_URL = "http://127.0.0.1:8000"



def login(username,password):

    response=requests.post(

        BASE_URL+"/api/v1/login",

        json={

            "username":username,

            "password":password

        }

    )

    return response.json()