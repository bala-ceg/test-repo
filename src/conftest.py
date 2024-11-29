# conftest.py
from dotenv import load_dotenv

def pytest_configure():
    load_dotenv('../.env.test', override=True)
