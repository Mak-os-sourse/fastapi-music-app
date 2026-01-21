from src.app.tests.config import settings_test
from src.app.tests.fake import fake

from src.app.service.storage import Storage

storage = Storage()

async def test_convert_file():
    path = settings_test.PATH_FILES / "user.jpg"
    await storage.convert(file=open(settings_test.PATH_FILES / "image.png", "rb").read(), new_path=path)

    assert path.exists()
    path.unlink()

async def test_write_file():
    text = fake.text()
    
    await storage.write_file(settings_test.PATH_FILES / "test_file.txt", text.encode())
    
    assert open(settings_test.PATH_FILES / "test_file.txt", "r").read() == text

async def test_read_file():
    text = fake.text()
    
    open(settings_test.PATH_FILES / "test_file.txt", "w").write(text)
    
    result = await storage.read_file(settings_test.PATH_FILES /"test_file.txt")
    
    assert result.decode() == text
    
async def test_delte_file():
    path = settings_test.PATH_FILES / "test_file.txt"
    text = fake.text()
    
    open(path, "w").write(text)
    
    await storage.delete_file(settings_test.PATH_FILES /"test_file.txt")
    
    assert not path.exists()

async def test_exists_file():
    text = fake.text()
    
    open(settings_test.PATH_FILES / "test_file.txt", "w").write(text)
    
    assert storage.exists_path(settings_test.PATH_FILES /"test_file.txt")