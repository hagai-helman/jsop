from setuptools import setup

setup(
    name='jsop',
    version='1.0.1',
    author='Hagai Helman Tov',
    author_email='hagai.helman@gmail.com',
    description='A way to store large amounts of JSON-style data on disk, and to access it quickly.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/hagai-helman/jsop',
    keywords=['JSON', 'dbm', 'persistence'],
    py_modules=['jsop'],
    license='MIT',
    install_requires=[],
    python_requires='~=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        ],
)
