from setuptools import setup

setup(
    name='jsop',
    version='0.5.0',
    author='Hagai Helman Tov',
    author_email='hagai.helman@gmail.com',
    description='A way to store large amounts of JSON-style data on disk, and to access it very quickly',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/hagai-helman/jsop',
    keywords=['JSON', 'dbm', 'persistence'],
    py_modules=['jsop'],
    license='MIT',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        ],
)
