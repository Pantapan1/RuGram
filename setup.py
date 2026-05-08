from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='rugram',
    version='0.1.2',
    description='Пиши Telegram-ботов на чистом русском Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pantapan1',
    url='https://github.com/Pantapan1/RuGram',
    packages=find_packages(),
    py_modules=['ядро', 'транспайлер'],
    entry_points={
        'console_scripts': [
            'rugram=транспайлер:главная',
        ],
    },
    install_requires=[
        'requests>=2.25',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
