from distutils.core import setup

setup(
    name='vk_messages',
    packages=['vk_messages'],
    license='MIT',
    version='1.3',
    description='Custom library to pass messages API restriction',
    author='Aragroth (Osiris)',
    author_email='aragroth.osiris@yandex.ru',
    url='https://github.com/Aragroth/vk_messages/',
    download_url='https://github.com/Aragroth/vk_messages/releases/tag/v1.3',
    keywords=['API', 'PYTHON', 'VK'],
    install_requires=[
        'requests',
        'bs4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
