from distutils.core import setup

setup(
    name='jsop',
    version='0.2.2',
    description='A dbm-based time-efficient persistence for large amount of JSON-style data',
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
