import zlib
from basic_types import Size

class WriteablePacket:
    def __init__(self):
        self.__data = bytearray()
        self.__index = 0
        self.encoding = 'utf-8'
        self.endian = 'little'

    def get_data(self) -> bytearray:
        return self.__data 
    
    def compress(self):
       self.__data = zlib.compress(self.__data)
    
    def decompress(self):
        self.__data = zlib.decompress(self.__data)

    def __write(self, data: bytes):
        self.__data.extend(data)

    def __write_int(self, value: int, length: int, signed):
        self.__write(value.to_bytes(length, self.endian, signed=signed))

    def write_string(self, value:str):
        data = bytes(value, encoding=self.encoding)
        self.write_uint(len(data))
        self.__write(data)
    
    def write_blob(self, name:str, value:bytes):
        self.write_string(name)
        self.write_uint(len(value))
        self.__write(value)
    
    def __read(self, length) -> bytes:
        offset = self.__index + length
        res = self.__data[self.__index:offset]
        self.__index = offset
        return res
    
    def read_blob(self) -> tuple:
        name = self.read_string()
        content = self.__read(self.read_uint())
        return (name, content)

    def read_int(self) -> int:      
        return int.from_bytes(self.__read(Size.INTEGER), self.endian, signed=True)
    
    def read_uint(self) -> int:
        return int.from_bytes(self.__read(Size.INTEGER), self.endian, signed=False)

    def read_string(self) -> str:
        return self.__read(self.read_uint()).decode(self.encoding)    

    def write_ushort(self, value: int):
        self.__write_int(value, Size.SHORT, signed=False)

    def write_short(self, value: int):
        self.__write_int(value, Size.SHORT, signed=True)

    def write_uint(self, value:int):
        self.__write_int(value, Size.INTEGER, signed=False)

    def write_int(self, value:int):
        self.__write_int(value, Size.INTEGER, signed=True)

    def write_ulong(self, value:int):
        self.__write_int(value, Size.LONG, signed=False)

    def write_long(self, value:int):
        self.__write_int(value, Size.LONG, signed=True)


class PackedData(WriteablePacket):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.entries = 0
        self.content = []

    def add_blob(self, path: str, blob: bytes):
        self.content.append((path, blob))
        self.entries += 1

    def pack(self):
        self.write_string(self.name)
        self.write_uint(self.entries)
        for path, blob in self.content:
            self.write_blob(path, blob)
        #self.compress()
      
    def unpack(self):
        """Unpack the name of the package and entries for the bytes"""
        self.name = self.read_string()
        self.entries = self.read_uint()

        print(f'name: {self.name}, entries: {self.entries}')
        for i in range(0, self.entries):
            self.content.append(self.read_blob())

def create_from_file(path: str) -> PackedData:
    """Create PackedData from an existing file and return it"""
    obj = PackedData()
        with open(path, mode='rb') as f:
        obj._WriteablePacket__data = f.read()
    obj.unpack()
    return obj