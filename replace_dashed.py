import json


def do_replaces(files, replaces):
    for filename in files:
        with open(filename, "r") as f:
            text = f.read()
        for replace_what, replace_how in replaces.items():
            text = text.replace(replace_what, replace_how)
        with open(filename, "w") as f:
            f.write(text)


print("To use this program you will need to copy errors with dashes to local file")
print("1) go to your service (f.e. https://vku.test.gosuslugi.ru/service/60018022/2.2.1003)")
print("2) open 'network' tab and try to play your service")
print("3) click right mouse button on POST 'play' method in 'network' tab, go to response, select 'raw' and copy that JSON")
print("4) open some local file and copy this JSON in this file")
# errors
errors_file = input("Input path to this file (POST 'play' request with dashes errors): ")
with open(errors_file, "r") as f:
    errors = f.read()
errors = [e["entityId"] for e in json.loads(errors)["versionDataErrors"]]
replaces = {e: e.replace("-", "_") for e in errors if "-" in e}

# files
files = [f.strip() for f in input("Input files, where to fix these errors; use comma as a seperator (f.e. 600000_Applicant.vm, tmp.tmp): ").split(",")]

# do
do_replaces(files, replaces)
