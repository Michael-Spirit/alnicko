import os
import datetime
import random


# generates test .pos file with ~4.2 Mb size
# and multiple .json files
if __name__ == '__main__':
    file_name = f'test-pos-file.pos'
    json_name = 'test-json-{}.json'

    if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + f'/{file_name}'):
        os.system(f'touch {file_name}')
    else:
        pass

    with open(file_name, 'w') as file:
        # header from .pos example
        file.write("% program   : RTKLIB ver.2.4.2\n")
        file.write("% inp file  : /tmp/68182893-5030-49ac-8324-5a7c67408291/Data/raw_201902191436/raw_201902191436.obs\n")
        file.write("% inp file  : /tmp/68182893-5030-49ac-8324-5a7c67408291/Data/raw_201902191414/raw_201902191414.obs\n")
        file.write("% inp file  : /tmp/68182893-5030-49ac-8324-5a7c67408291/Data/raw_201902191436/raw_201902191436.nav\n")
        file.write("% inp file  : /tmp/68182893-5030-49ac-8324-5a7c67408291/Data/raw_201902191436/raw_201902191436.sbs\n")
        file.write("% obs start : 2019/02/19 14:37:08.0 GPST (week2041 225428.0s)\n")
        file.write("% obs end   : 2019/02/19 15:37:15.0 GPST (week2041 229035.0s)\n")
        file.write("% ref pos   : 32.039210041  34.816553703  305.5207\n")
        file.write("% \n")
        file.write("% (lat/lon/height=WGS84/ellipsoidal,Q=1:fix,2:float,3:sbas,4:dgps,5:single,6:ppp,ns=# of satellites)\n")
        file.write("%  GPST                  latitude(deg) longitude(deg)  height(m)   Q  ns   sdn(m)   sde(m)   sdu(m)  sdne(m)  sdeu(m)  sdun(m) age(s)  ratio\n")

        now = datetime.datetime(2019, 1, 1)
        for _ in range(30000):
            now = now + datetime.timedelta(microseconds=random.randint(500_000, 2_000_000))
            file.write(f"{now.strftime('%Y/%m/%d %H:%M:%S.%f')}   32.041449250   34.816069084    57.1309   1   6   6.2565  18.5049  24.1780   7.4584 -19.6609 -10.9075   0.19    4.3\n")

    for x in range(5):
        if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/' + json_name.format(x)):
            os.system(f'touch {json_name.format(x)}')
        else:
            pass
