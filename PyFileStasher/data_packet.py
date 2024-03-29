import zlib
from basic_types import Size
from os.path import join

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
        
    def get_compressed(self) -> bytearray:
        """Return the written bytes as zlib compressed"""
        return zlib.compress(self.__data)
    
    def decompress(self, bytes: bytearray) -> bytearray:
        """Return the provided bytes as zlib decompressed"""
        return zlib.decompress(bytes)

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
    def __init__(self, name=''):
        super().__init__()
        self.name = name
        self.entries = 0
        self.content = []
        self.isPacked = False

    def add_blob(self, path: str, blob: bytes):
        """Add a blob to the list of content to be packed"""
        self.content.append((path, blob))
        self.entries += 1

    def pack(self):
        """Pack all the content into an array of bytes"""
        self.write_string(self.name)
        self.write_uint(self.entries)
        for path, blob in self.content:
            self.write_blob(path, blob)
        self.isPacked = True
      
    def unpack(self):
        """Unpack the name of the package and entries for the bytes"""
        self.name = self.read_string()
        self.entries = self.read_uint()

        for i in range(0, self.entries):
            self.content.append(self.read_blob())

def create_file_from_obj(obj: PackedData, path='', file_name='content.bin'):
    """Create a binary file from a PackedData object"""
    if not obj.isPacked:
        print(f'Attempted to write: {file_name} but data was not packed... Packing data now')
        obj.pack()

    with open(join(path, file_name), mode='wb') as f:
        f.write(obj.get_data())

def create_obj_from_file(path: str) -> PackedData:
    """Create PackedData from an existing file and return it"""
    obj = PackedData()
    with open(path, mode='rb') as f:
        obj._WriteablePacket__data = f.read()
    obj.unpack()
    obj.isPacked = True
    return obj

def create_blobs_from_obj(obj: PackedData, dest_path: str):
    """Create blobs/files from a PackedData object and write them to the specified path"""
    for file, data in obj.content:
        with open(join(dest_path, file), mode='w+b') as f:
            f.write(data)

def create_blobs_from_file(target_path: str, dest_path=''):
    """Create blobs/files from a file at target_path and write them to the dest_path"""
    obj = create_obj_from_file(target_path)
    for file, data in obj.content:
        with open(join(dest_path, file), mode='w+b') as f:
            f.write(data)