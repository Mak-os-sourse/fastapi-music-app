from pathlib import Path
import asyncio

async def cp_file(path: str, new_path: str):
    with open(path, "rb") as source:
        with open(new_path, "wb") as result:
            result.write(source.read())

async def await_file(path: str) -> bool:
    path = Path(path)
    for _ in range(30):
        if path.exists():
            return True
        await asyncio.sleep(0.1)
    return False