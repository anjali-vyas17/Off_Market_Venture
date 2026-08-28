from setuptools import setup, find_packages

with open("requirements.txt", "w") as f:
	f.write("frappe\n")

setup(
	name="stock_crm",
	version="1.0.0",
	description="Share Market CRM for Unlisted Equity Trading, Deal Ledgers & Tax Compliance",
	author="Off Market Venture",
	author_email="admin@offmarketventure.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=["frappe"],
)
