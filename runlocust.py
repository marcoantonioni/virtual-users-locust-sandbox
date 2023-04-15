import os, sys
from locust.main import main as mainLocust

if __name__ == "__main__":
    mainLocust()

# python ./runlocust.py --config=./configurations/baw-vu-cfg-1.conf