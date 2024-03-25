filename = input("File: ")
replaces = {"A2", "A3"}

with open(filename, "w") as f:
    text = f.read()
    for replace_what, replace_how in replaces:
        text.replace(replace_what, replace_how)
    f.write(text)
