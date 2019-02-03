from distutils.core import setup

setup(
    name='jsop',
    version='0.1',
    description='A dbm-based time-efficient persistence for large amount of JSON-style data',
    long_description="""This package can be used instead of JSON where the amount of data makes the I/O operartions too slow. Also, it is designed to enable easy migration of data in existing applications, with minimal code changes.
""",
    url='https://github.com/hagai-helman/jsop',
    keywords=['JSON', 'dbm', 'persistence'],
    packages=['jsop'],
    license='MIT',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        ],
)
