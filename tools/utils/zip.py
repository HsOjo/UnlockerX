import os
import re
from zipfile import ZipFile


def zip_directory(path_dir, path_zip, filter_=None, remove=None, dirname=None):
    reg_filter = None
    reg_remove = None

    if filter_ is not None:
        reg_filter = re.compile(filter_)
    if remove is not None:
        reg_remove = re.compile(remove)

    path_dir = os.path.abspath(path_dir)
    with ZipFile(path_zip, 'w') as zf:
        for d, ds, fs in os.walk(path_dir):
            z_d = d.replace(path_dir, '')
            for f in fs:
                path = os.path.join(d, f)
                z_path = os.path.join(z_d, f).strip(os.path.sep)

                if reg_filter is not None and not reg_filter.match(z_path):
                    continue

                if reg_remove is not None and reg_remove.match(z_path):
                    continue

                if dirname is True:
                    dirname = os.path.basename(path_dir)
                if dirname is not None:
                    z_path = '%s/%s' % (dirname, z_path)

                zf.write(path, z_path)
