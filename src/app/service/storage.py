import aiofiles

from pathlib import Path
from ffmpeg.errors import FFmpegError
from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress

from src.app.config import settings

class Storage():
    async def convert(self, file: bytes, new_path: str, prefix: str = "source", **args):
        list_dir = str(new_path).split("/", -1)
        name = list_dir.pop().split(".", -1)
        path = Path("/".join(list_dir))

        source_path = path / f"{name[0]}-{prefix}.{name[-1]}"
        
        await self.write_file(source_path, file)
        try:
            await self.ffmpeg_convert(source_path, new_path, **args)
        except FFmpegError as e:
            print(e)
        finally:
            await self.delete_file(source_path)
    
    def exists_path(self, path: str) -> bool:
        path = Path(path)
        return path.exists()
    
    async def delete_file(self, path: str):
        path = Path(path)
        path.unlink()
    
    async def write_file(self, path: str, data: bytes):
        async with aiofiles.open(path, "wb") as file:
            await file.write(data)

    async def read_file(self, path: str, seek: int = 0, size: int = -1) -> bytes:
        async with aiofiles.open(path, "rb") as file:
            await file.seek(seek)
            return await file.read(size)

    async def ffmpeg_convert(self, input_file: str, output_file: str, **args) -> bytes:
        ffmpeg = FFmpeg().option("y").input(str(input_file)).output(output_file, **args)
        
        @ffmpeg.on("progress")
        def time_to_terminate(progress: Progress):
            print(progress)

        return await ffmpeg.execute()
    
storage = Storage()