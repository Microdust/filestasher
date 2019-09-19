from glob import glob
import zlib
from data_packet import PackedData
from os.path import join
        
if __name__ == "__main__":
    pack = PackedData()
    pack.name = "Hello world"

    for file in glob('content/*'):
        print(file)
        with open(file, mode='rb') as f:
            pack.add_blob(file, f.read())
    pack.pack()
    
    with open('test.bin', mode='wb') as f:
        f.write(pack.get_data())

    new_pack = PackedData()
    new_pack.load_file('test.bin')
    
    for file, data in new_pack.content:
        path = join('parsed', file)
        with open(path, mode='w+b') as f:
            f.write(data)