from setuptools import setup, find_packages

dep = [
    "tqdm==4.36.1",
    "matplotlib==3.1.2",
    "networkx==1.9.1",
    "scikit-learn==0.21.3",
    "scipy==1.3.1",
    "numpy==1.17.2",
]

setup(name="community-detection",
      version="1.0.0",
      description="community-detection",
      url="None",
      packages=find_packages(exclude=[]),
      include_package_data=True,
      install_requires=dep,
      )
