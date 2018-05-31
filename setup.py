from setuptools import setup

setup(name='eurekatrees',
      version='0.3',
      description='Spark MLLib debug string converter to visualization',
      url='http://github.com/ChuckWoodraska/EurekaTrees',
      author='Chuck Woodraska',
      author_email='chuck.woodraska@gmail.com',
      license='MIT',
      packages=['eurekatrees'],
      install_requires=[
          'jinja2',
      ],
      entry_points={
          'console_scripts': ['eurekatrees=eurekatrees.eurekatrees:main'],
      },
      include_package_data=True,
      zip_safe=False)