from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [
        line for line in f.read().strip().split("\n")
        if line and not line.startswith("#")
    ]

setup(
    name="logistics_transport_erp",
    version="0.0.1",
    description="Full-stack logistics & transportation ERP for India",
    author="Your Company",
    author_email="dev@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
