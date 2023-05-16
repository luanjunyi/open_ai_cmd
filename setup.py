from setuptools import setup, find_packages

setup(
    name="term_chat_gpt",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "qq = term_chat_gpt.main:qq",
            "gpt = term_chat_gpt.main:chat_full_loop",
            "google = term_chat_gpt.main:google",
            "web = term_chat_gpt.main:fetch_web",
        ],
    },
    python_requires=">=3.9",
)
