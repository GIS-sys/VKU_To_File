import json
import os
import requests
import subprocess


DATA_FILENAME = "tmp.tmp"


def compareStrings(s1, s2):
    for i in range(min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            return f"Not the same at index={i}. Parts from i-5 to i+15: {s1[i-5:i+15]}, {s2[i-5:i+15]}"
    return "Strings are the same"


class String:
    def __init__(self, string):
        self.string = string
        self.parsed = dict()

    def indexOf(self, substring):
        index = len(self.string)
        if substring in self.string:
            index = self.string.index(substring)
        return index

    def goTo(self, substring):
        index = self.indexOf(substring)
        self.string = self.string[index:]
        return self

    def goOver(self, substring):
        index = self.indexOf(substring) + len(substring)
        self.string = self.string[index:]
        return self

    def readUntil(self, substring, name=None):
        index = self.indexOf(substring)
        found = self.string[:index]
        if not (name is None):
            if not (name in self.parsed):
                self.parsed[name] = []
            self.parsed[name].append(found)
        return self

    def readAndGoTo(self, substring, name=None):
        return self.readUntil(substring, name).goTo(substring)

    def readAndGoOver(self, substring, name=None):
        return self.readUntil(substring, name).goOver(substring)

    def skip(self, number=None, substring=None):
        if not (number is None) and not (substring is None):
            raise Exception("String.skip got number!=None, substring!=None")
        if number is None and substring is None:
            number = 1
        if not (substring is None):
            if not self.string.startswith(substring):
                raise Exception(f"String.skip - no '{substring}' found")
            number = len(substring)
        self.string = self.string[number:]
        return self

    def startswith(self, substring):
        return self.string.startswith(substring)


class Request:
    def __init__(self, real_curl):
        self._origin_curl = real_curl
        self.fromCurl(real_curl)

    def fromCurl(self, curl_string):
        parsing = String(curl_string)
        parsing.skip(substring="curl '").readAndGoOver("' ", name="url")
        parsing.skip(substring="--compressed -X PUT ")
        while not parsing.startswith("--data-raw"):
            arg = parsing.readAndGoOver(" '", "arg").parsed['arg'][-1]
            parsing.readAndGoOver("' ", arg)
        parsing.skip(substring="--data-raw $'")
        self.parsed = parsing.parsed
        self.parsed.pop("arg")
        self.parsed["--data-raw"] = [parsing.string[:-1]]

    def toCurl(self):
        res = "curl '" + self.parsed["url"][0] + "' "
        res += "--compressed -X PUT "
        for arg_name, arg_list_val in self.parsed.items():
            if arg_name in ["url", "--data-raw"]:
                continue
            for arg_val in arg_list_val:
                res += f"{arg_name} '{arg_val}' "
        res += "--data-raw $'" + self.parsed['--data-raw'][0] + "'"
        return res

    def __repr__(self):
        res = "Request\n"
        for k, v in self.parsed.items():
            res += f"{k}: {v}" + "\n"
        return res

    def send(self):
        url = self.parsed["url"][0]
        headers = {}
        for header in self.parsed["-H"]:
            hlabel = header[:header.index(":")].strip()
            htext = header[header.index(":")+1:].strip()
            headers[hlabel] = htext
        data = self.parsed["--data-raw"][0]
        response = requests.put(url, headers=headers, json=json.loads(data.encode('utf-8').decode('unicode_escape')))
        print(response.code)


class Data:
    def __init__(self, req):
        self.req = req
        self.data = {}
        self.parse()

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type is None:
            self.save()

    def save(self):
        string_dumped = json.dumps(self.data, separators=[',', ':'])
        string_dumped = string_dumped.replace("\\", "\\\\").replace("'", "\\'")
        self.req.parsed["--data-raw"] = [string_dumped]

    def parse(self):
        string_parsed = self.req.parsed["--data-raw"][0]
        string_parsed = string_parsed.encode('utf-8').decode('unicode_escape')
        self.data = json.loads(string_parsed)

    def __repr__(self):
        return json.dumps(self.data, indent=1)

    def saveToFile(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(self.data, indent=4))

    def loadFromFile(self, filename):
        with open(filename, "r") as f:
            self.data = json.loads(f.read())
        os.remove(filename)


print("To use this program you will need to copy data from service on VKU to local file")
print("1) go to your service (f.e. https://vku.test.gosuslugi.ru/service/60018022/2.2.1003)")
print("2) open 'network' tab and make some simple change in your service")
print("3) click right mouse button on PUT method in 'network' and choose 'copy as CURL'")
print("4) open some local file and copy this curl in this file")
curl_filename = input("Input path to this file (PUT request when making change in browser, saved as CURL): ")
if curl_filename == "":
    curl_filename = "example.tmp"
with open(curl_filename, "r") as f:
    curl_text = f.read()[:-1]

req = Request(curl_text)
with Data(req) as data:
    data.saveToFile(DATA_FILENAME)
    input(f"Service was mirrored into file {DATA_FILENAME}. Change data there, then press any button to push it back into cloud")
    data.loadFromFile(DATA_FILENAME)
req.send()

