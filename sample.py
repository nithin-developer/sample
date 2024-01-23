import requests
from utils.storage import get_token

class AuthBase:
    
    def get_auth_headers(self):
        return {
            "Authorization": f"Basic {get_token()}"
        }
    
    def get(self, url, params = {}):
        auth_headers = self.get_auth_headers()
        response = requests.get(url, params=params, headers=auth_headers)
        if response.status_code < 400:
            return response.data
        else:
            # logger.error(f"{response.status_code}")
            return False
        
    def post(self, url, data = {}):
        auth_headers = self.get_auth_headers()
        response = requests.post(url, data=data, headers=auth_headers)
        if response.status_code < 400:
            return response.data
        else:
            # logger.error(f"{response.status_code}")
            return False

class AuthAPI(AuthBase):

    @classmethod
    def register(self, username, email, password, firstName, lastName):
        base_url = "https://api.ems-emp.worksnet.in/api/v1/auth/signup"
        tenantName = "HP TECH"
        containerName = "hptech"
        zoneId = "eastus"
        connectionUrl = "mongodb://localhost:27017/emsourcedev"
        subDomain = "hptech"
        response = self.post(
            base_url,
            data={
                "email": email,
                "username": username,
                "password": password,
                "firstName": firstName,
                "lastName": lastName,
                "tenantName": tenantName,
                "containerName": containerName,
                "zoneId": zoneId,
                "connectionUrl": connectionUrl,
                "subDomain": subDomain,
            }
        )
        if response.status_code == 200:
            return response.data
        else:
            return False


    @classmethod
    def login(self, email, password):
        base_url = "https://api.ems-emp.worksnet.in/api/v1/auth/login"
        response = self.post(
            base_url,
            data={
                "email": email,
                "password": password,
            }
        )
        if response.status_code == 200:
            return response.data
        else:
            return False


    @classmethod
    def GetRefereshToken(self, mac_address, os_version, os_type):
        base_url = "https://api.ems-emp.worksnet.in/api/v1/auth/refresh-token"
        response = self.post(
            base_url,
            data={
                "mac_address": mac_address,
                "os_version": os_version,
                "os_type": os_type,
            }
        )
        if response.status_code == 200:
            return response.data
        else:
            return False


    @classmethod
    def ForgetPassword(self, email):
        base_url = "https://api.ems-emp.worksnet.in/api/v1/auth/forgot-password"
        response = self.post(
            base_url,
            data={
                "email": email,
            }
        )
        if response.status_code == 200:
            return response.data
        else:
            return False
        
    
    @classmethod
    def SetPassword(self, secretToken, password):
        base_url = f"https://api.ems-emp.worksnet.in/api/v1/auth/set-password/{secretToken}"
        response = self.post(
            base_url,
            data={
                "password": password
            }
        )
        if response.status_code == 200:
            return response.data
        else:
            return False