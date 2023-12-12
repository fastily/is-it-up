import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="is_it_up",
    version="0.0.1",
    author="Fastily",
    author_email="fastily@users.noreply.github.com",
    description="Queries a site to check if it is accessible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastily/is-it-up",
    project_urls={
        "Bug Tracker": "https://github.com/fastily/is-it-up/issues",
    },
    include_package_data=True,
    packages=setuptools.find_packages(include=["is_it_up"]),
    install_requires=['cachetools', 'fastapi[all]', 'gunicorn', 'httpx[http2]', 'spawn-user-agent'],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
