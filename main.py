import yaml

import config
import uq


if __name__ == '__main__':
    mp = uq.MainPage()
    mp.parse()
    config.write_main()
