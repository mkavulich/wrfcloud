from setuptools import setup

setup(
    name='wrfcloud',
    version='0.0.3',
    description='NCAR/RAL WRF Cloud Framework',
    author='David Hahn',
    author_email='hahnd@ucar.edu',
    maintainer='David Hahn',
    maintainer_email='hahnd@ucar.edu',
    packages=['wrfcloud', 'wrfcloud/api', 'wrfcloud/aws', 'wrfcloud/dynamodb', 'wrfcloud/user', 'wrfcloud/runtime', 'wrfcloud/runtime/tools'],
    install_requires=[
        'boto3>=1.24.8',
        'botocore>=1.27.8',
        'pyyaml>=5.4',
        'bcrypt>=3.2.0',
        'PyJWT>=2.4.0',
        'aws-parallelcluster==3.0.2',
        'f90nml>=1.4',
        'netCDF4>=1.5.0',
        'matplotlib>=3.3.0',
        'numpy>=1.23.0'
    ],
    package_dir={'wrfcloud': 'wrfcloud'},
    package_data={
        'wrfcloud': [
            'resources/env_vars.yaml',
            'resources/logo.jpg',
            'resources/password_reset.html',
            'resources/welcome_email.html',
            'imagebuilder/imagebuilder.yaml',
            'user/table.yaml',
            'aws/resources/cf_imagebuilder_wrf_intel.yaml',
            'aws/resources/cluster.wrfcloud.yaml'
        ]
    },
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'wrfcloud-imagebuilder=wrfcloud.aws.imagebuilder:main',
            'wrfcloud-cluster=wrfcloud.aws.pcluster:main',
            'wrfcloud-run=wrfcloud.runtime.run:main',
            'wrfcloud-geojson=wrfcloud.runtime.tools.geojson:main'
        ]
    }
)
