from setuptools import setup, find_packages

setup(
    name='rugram',
    version='0.1.0',
    description='Пиши Telegram-ботов на чистом русском языке',
    long_description='RuGram — транспайлер и библиотека для создания ботов с синтаксисом и Чебурашкой под капотом',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'rugram=rugram.транспайлер:главная',
        ],
    },
    install_requires=[
        'requests>=2.25',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Russian',  # Шутка, но почему нет?
    ],
)