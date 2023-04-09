# virtual-users-locust-sandbox

Sandbox per struttura progetto finale

```
# moduli
pip install locust
pip install jproperties

BASE_HOST=https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud

IAM_HOST=https://cp-console-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud


locust --headless --autostart --only-summary --run-time 5s --users 1 --host https://cp-console-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud

```

