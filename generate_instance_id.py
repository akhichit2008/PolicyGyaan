import random
from pathlib import Path
import sys

def generate_instance_id(id_len=10):
    iid = random.sample("abcdefghijklmnopqrstuvwxyz1234567890;/-[]~!#$@%^&*()",10)
    instance_id = ""
    for c in iid:
        instance_id += c
    return instance_id

def write_env(instance_id):
    f = open(".env","a+")
    f.seek(0)
    data = f.read()
    print(data)
    if "APP_INSTANCE_ID" not in data:
        f.write(f"\nAPP_INSTANCE_ID={instance_id}")
        print("[SUCCESS] :- APPLICATION INSTANCE ID Created!!!")
    else:
        print("[WARNING] :- APPLICATION INSTANCE ID Already Exists!!!")

    exit(0)


if not Path(".env").is_file():
    print("[ERROR] :- Create .env File to Proceed!!!!")
    exit(1)

if len(sys.argv) > 1:
    instance_id = generate_instance_id(id_len=sys.argv[1])
    write_env(instance_id)

else:
    instance_id = generate_instance_id(id_len=10)
    write_env(instance_id)

