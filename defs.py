from pathlib import Path
import sys
import os.path
import resource

path = Path(os.path.dirname(__file__))
PROJ_ROOT = str(path)+'/work'
DATA = PROJ_ROOT+'/data'
ORIGINAL_DATA = DATA+'/original'
ORIGINAL_PKL_DATA = DATA+'/original_pkl'
INTERIM_DATA = DATA+'/interim'

DATASOURCE = PROJ_ROOT+'/datasource'

LIB = PROJ_ROOT+'/lib'
DOCS = PROJ_ROOT+'/docs'
SRC = PROJ_ROOT+'/src'
TMP = PROJ_ROOT+'/tmp'
FILE = PROJ_ROOT+'/files'
IMAGES = FILE+'/images'
CONFIG = PROJ_ROOT+'/config'
LOG = PROJ_ROOT+'/log'



sys.path = list(set(sys.path))
sys.path.append(LIB)
sys.path.append(DATASOURCE)
sys.path.append(DATASOURCE+'/interim')
sys.path.append(DATASOURCE+'/original')
sys.path.append(DATASOURCE+'/other')
sys.path.append(SRC)

def get_info(target_df):
    max_row = len(target_df)

    df = target_df.dtypes.to_frame()

    df.columns = ['DataType']
    print('Calculating Count')
    df['Count'] = target_df.shape[0]
    print('Calculating Null')
    df['Null'] = target_df.isnull().sum()
    print('Calculating Null%')
    df['Null%'] = (df['Null'] / max_row * 100).round(1)
    # print('Calculating Unique')
    # df['Unique'] = target_df.nunique()
    # print('Calculating Unique%')
    # df['Unique%'] = (df['Unique'] / max_row * 100).round(1)
    # print('Calculating Min')
    # df['Min'] = target_df.min()
    # print('Calculating Max')
    # df['Max'] = target_df.max()
    # df['Average'] = df.average()
    return df



def set_memory_limit(memory_kilobytes):
    # ru_maxrss: peak memory usage (bytes on OS X, kilobytes on Linux)
    usage_kilobytes = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rlimit_increment = 1024 * 1024
    resource.setrlimit(resource.RLIMIT_DATA, (rlimit_increment, resource.RLIM_INFINITY))

    memory_hog = []

    while usage_kilobytes() < memory_kilobytes:
        try:
            for x in range(100):
                memory_hog.append('x' * 400)
        except MemoryError as err:
            rlimit = resource.getrlimit(resource.RLIMIT_DATA)[0] + rlimit_increment
            resource.setrlimit(resource.RLIMIT_DATA, (rlimit, resource.RLIM_INFINITY))



