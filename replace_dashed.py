import json


def do_replaces(files, replaces):
    for filename in files:
        with open(filename, "r") as f:
            text = f.read()
        for replace_what, replace_how in replaces.items():
            text = text.replace(replace_what, replace_how)
        with open(filename, "w") as f:
            f.write(text)


# errors
errors_file = input("File with play errors with dashes")
with open(errors_file, "r") as f:
    errors = f.read()
print(errors[2980:3050])
errors = [e["entityId"] for e in json.loads(errors)["versionDataErrors"]]
replaces = {e: e.replace("-", "_") for e in errors if "-" in e}

# files
files = [f.strip() for f in input("Files: ").split(",")]

# do
do_replaces(files, replaces)