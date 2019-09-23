# This is an example of how to use filestasher
from glob import glob
from data_packet import PackedData, create_obj_from_file, create_file_from_obj, create_blobs_from_file, create_blobs_from_obj
from os.path import join
        
if __name__ == "__main__":
    # Create a PackedData object, the name is written to the internal byte array
    data = PackedData(name='hello_world')

    # Get a list of blobs to write to the PackedData object
    for file in glob('content/*'):
        print(file)
        with open(file, mode='rb') as f:
            # add binary data from the blob to the PackedData object
            data.add_blob(file, f.read())
    
    # When done adding to the PackedData object call pack() to write the binary values
    data.pack() 

    # Create a file from the PackedData object
    create_file_from_obj(data)

    # Create a new PackedData object from the just created file
    new_obj = create_obj_from_file('content.bin')

    # Create blobs/files from either the file or PackedData object
    create_blobs_from_obj(new_obj, 'parsed')
    create_blobs_from_file('content.bin', 'parsed')