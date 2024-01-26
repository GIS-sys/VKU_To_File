import requests


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


real_curl = input("Insert CURL from browser, when you change the service and browser tries to save it:\n")
req = Request(real_curl)
print(compareStrings(req._origin_curl, req.toCurl()))

