import shutil, os
from pathlib import Path

path = "/"

total, used, free = shutil.disk_usage(path)


print(f"전체 용량: {total // (2**30)} GiB")
print(f"사용 중:   {used  // (2**30)} GiB")
print(f"남은 용량: {free  // (2**30)} GiB")