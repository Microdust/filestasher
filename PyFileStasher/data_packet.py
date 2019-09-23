import zlib
from basic_types import Size

class WriteablePacket:
    """Data handling object"""
    def __init__(self, encoding='utf-8', endian='little', data=bytearray()):
        self.__data = data
        self.__index = 0
        self.__encoding = encoding
        self.__endian = endian

    def get_data(self) -> bytearray:
        """Return the written bytes"""
        return self.__data 
    
    def compress(self):
       self.__data = zlib.compress(self.__data)
    
    def decompress(self):
        self.__data = zlib.decompress(self.__data)

    def __write(self, data: bytes):
        """Internal function to write bytes directly to the writeable packet"""
        self.__data.extend(data)

    def __write_int(self, value: int, length: int, signed):
        """Internal function to write integers directly to the writeable packet"""
        self.__write(value.to_bytes(length, self.__endian, signed=signed))

    def write_string(self, value:str):
        """Write a string to the writeable packet"""
        data = bytes(value, encoding=self.__encoding)
        self.write_uint(len(data))
        self.__write(data)
    
    def write_blob(self, name:str, value:bytes):
        """Write a binary object to the writeable packet"""
        self.write_string(name)
        self.write_uint(len(value))
        self.__write(value)
    
    def __read(self, length) -> bytes:
        """Internal function to read bytes from the writeable packet"""
        offset = self.__index + length
        res = self.__data[self.__index:offset]
        self.__index = offset
        return res
    
    def read_blob(self) -> tuple:
        """Read a blob from the data and return it as a tuple -> (name, bytes)"""
        name = self.read_string()
        content = self.__read(self.read_uint())
        return (name, content)

    def read_ushort(self) -> int:
        """Read and return an unsigned short from the data"""      
        return int.from_bytes(self.__read(Size.SHORT), self.__endian, signed=False)

    def read_short(self) -> int:
        """Read and return a signed short from the data"""      
        return int.from_bytes(self.__read(Size.SHORT), self.__endian, signed=True)

    def read_uint(self) -> int:
        """Read and return an unsigned integer from the data"""  
        return int.from_bytes(self.__read(Size.INTEGER), self.__endian, signed=False)

    def read_int(self) -> int:      
        """Read and return a signed integer from the data"""      
        return int.from_bytes(self.__read(Size.INTEGER), self.__endian, signed=True)
    
    def read_ulong(self) -> int:
        """Read and return an unsigned long from the data"""  
        return int.from_bytes(self.__read(Size.LONG), self.__endian, signed=False)
    
    def read_long(self) -> int:
        """Read and return a signed long from the data"""  
        return int.from_bytes(self.__read(Size.LONG), self.__endian, signed=True)

    def read_string(self) -> str:
        """Read and return a string from the data""" 
        return self.__read(self.read_uint()).decode(self.__encoding)    

    def write_ushort(self, value: int):
        """Write an usigned short to the data"""
        self.__write_int(value, Size.SHORT, signed=False)

    def write_short(self, value: int):
        """Write a signed short to the data"""
        self.__write_int(value, Size.SHORT, signed=True)

    def write_uint(self, value:int):
        """Write an unsigned integer to the data"""
        self.__write_int(value, Size.INTEGER, signed=False)

    def write_int(self, value:int):
        """Write a signed integer to the data"""
        self.__write_int(value, Size.INTEGER, signed=True)

    def write_ulong(self, value:int):
        """Write an unsigned long to the data"""
        self.__write_int(value, Size.LONG, signed=False)

    def write_long(self, value:int):
        """Write a signed long to the data"""
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