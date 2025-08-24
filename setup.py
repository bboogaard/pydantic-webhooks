from setuptools import setup


setup(name='pydantic-webhooks',
      version='0.1.0',
      description='Pydantic webhooks',
      url='https://github.com/bboogaard/pydantic-webhooks',
      author='Bram',
      author_email='padawan@hetnet.nl',
      license='MIT',
      packages=['pydantic_webhooks'],
      install_requires=[
          'python-dotenv==1.0.1',
          'pydantic==v2.11.7',
          'typer==0.16.0',
          'pytz==2025.2',
          'requests==2.32.5',
      ],
      zip_safe=False)
