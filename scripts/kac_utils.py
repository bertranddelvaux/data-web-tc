import urllib.parse



def split_url_flexible_with_extension_check(url_string):
    """Splits a URL-like string into base URL, folder, and file components.
    If the last part of the path has no extension, it's considered a folder.

    Args:
        url_string: The URL string or path-like string to split.
                    Can be None, an empty string, a path, or a full URL.

    Returns:
        A dictionary containing 'url', 'folder', and 'file' components.
        Values will be None or empty strings if the corresponding part
        cannot be identified.
    """
    if not url_string:
        return {'url': '', 'folder': '', 'file': ''}

    try:
        parsed_url = urllib.parse.urlparse(url_string)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        path = parsed_url.path.lstrip('/')

        base_url = f"{scheme}://{netloc}/" if scheme and netloc else ''

        parts = path.split('/')

        if parts:
            last_part = parts[-1]
            if '.' not in last_part:  # No extension, consider it part of the folder
                folder = '/'.join(parts) #+ '/'
                file = ''
            elif len(parts) > 1:
                folder = '/'.join(parts[:-1]) + '/'
                file = last_part
            else:  # Only one part with an extension, it's a file at the root
                folder = ''
                file = last_part
        else:
            folder = ''
            file = ''
        return {
            'url': base_url,
            'folder': folder,
            'file': file
        }
    except Exception:
        # If parsing as a full URL fails, try treating the input as a path
        path = url_string.lstrip('/')
        parts = path.split('/')
        if parts:
            last_part = parts[-1]
            if '.' not in last_part:  # No extension, consider it a folder
                folder = '/'.join(parts) + '/'
                file = ''
            elif len(parts) > 1:
                folder = '/'.join(parts[:-1]) + '/'
                file = last_part
            else:  # Single part with extension, it's a file
                folder = ''
                file = last_part
        else:
            folder = ''
            file = ''
        return {'url': '', 'folder': folder, 'file': file}


class MappingKAC:

    def __init__(self, mapping=None):
        self.forward = {}
        self.backward = {}
        if mapping:
            self.update(mapping)

    def add(self, key1, key2):
        self.forward[key1] = key2
        self.backward[key2] = key1
        # in case the key does not end with '/', neither with a file, add its version with '/'
        split = split_url_flexible_with_extension_check(key1)
        if split['file'] == '' and split['folder'] != '' and split['folder'][-1] != '/':
            self.forward[key1 + '/'] = key2 + '/'
            self.backward[key2 + '/'] = key1 + '/'

    def get_forward(self, key1):
        if isinstance(key1, str):
            return self._get_forward(key1)
        elif isinstance(key1, list) and all(isinstance(item, str) for item in key1):
            return [self._get_forward(k) for k in key1]
        else:
            raise NotImplementedError(f'key1 {key1} neither a string, nor a list of strings')

    def get_backward(self, key2):
        if isinstance(key2, str):
            return self._get_backward(key2)
        elif isinstance(key2, list) and all(isinstance(item, str) for item in key2):
            return [self._get_backward(k) for k in key2]
        else:
            raise NotImplementedError(f'key2 {key2} neither a string, nor a list of strings')

    def _get_forward(self, key1):
        split1 = split_url_flexible_with_extension_check(key1)
        url = self.forward.get(split1['url'])
        folder = self.forward.get(split1['folder'])
        file = split1['file']
        if self.forward.get(split1['file']) is None and file != '':
            file = file.replace('_SLOSH.nc', '.nc').replace('taostc_', '').replace('taos_', 'tc_')
            file = ('tc_' if 'tc_' not in file else '') + file
        else:
            file = self.forward.get(split1['file'])
        return (url if url else '') + (folder if folder else '') + (file if file else '')

    def _get_backward(self, key2):
        split2 = split_url_flexible_with_extension_check(key2)
        url = self.backward.get(split2['url'])
        folder = self.backward.get(split2['folder'])
        file = split2['file']
        if self.backward.get(split2['file']) is None and file != '':
            file = file.replace('.nc', '_SLOSH.nc')
            if 'windwater' in file:
                file = file.replace('tc_', 'taos_')
            elif 'tc' in file:
                if '30s' in folder or 'tc_realtime' in folder:
                    file = file.replace('tc_', 'taostc_')
                elif '15as' in folder:
                    file = file.replace('tc_', '')
        else:
            file = self.backward.get(split2['file'])
        return (url if url else '') + (folder if folder else '') + (file if file else '') # + ('/' if folder and file else '')

    def update(self, mapping):
        for key1, key2 in mapping.items():
            self.add(key1, key2)


mappingKAC = MappingKAC({
    # url
    'https://www.kacportal.com/': 'https://kac.kacportal.com/',
    # folders
    'portal/kacs3/arc/mpres_data': 'portal/data/arc',
    'portal/kacs3/arc/mpres_data/archive': 'portal/data/arc/archive',
    'portal/kacs3/arc/mpres_data/postevent': 'portal/data/arc/postevent',
    # 'portal/kacs3/arc/mpres_data/poststorm': 'portal/data/arc/postevent',
    'portal/kacs3/arc/tc_realtime': 'portal/data/arc/tc_realtime',
    'portal/kacs3/arc/mpres_data/postevent/ofcl_15as_nc': 'portal/data/arc/postevent/tc_ofcl_15as_nc',
    'portal/kacs3/arc/mpres_data/postevent/taos_swio30s_ofcl_windwater_nc': 'portal/data/arc/postevent/tc_swio30s_ofcl_windwater_nc',
    'portal/kacs3/arc/mpres_data/postevent/taos_swio30s_ofcl_windwater_shp': 'portal/data/arc/postevent/tc_swio30s_ofcl_windwater_shp',
    # folders part
    'ofcl_15as_nc': 'tc_ofcl_15as_nc',
    'taos_swio30s_ofcl_windwater_nc': 'tc_swio30s_ofcl_windwater_nc',
    'taos_swio30s_ofcl_windwater_shp': 'tc_swio30s_ofcl_windwater_shp',
    # files
    'daily_xsr_shp.zip': 'xr_daily_shp.zip',
    # 'daily_xsr_shp.zip.sha256': 'xr_daily_shp.zip.sha256',
    'taos_swio30s_ofcl_windwater_shp.zip': 'tc_swio30s_ofcl_windwater_shp.zip',
    # 'taos_swio30s_ofcl_windwater_shp.zip.sha256': 'tc_swio30s_ofcl_windwater_shp.zip.sha256',
    'taos_swio_ofcl_storms_shp.zip': 'tc_swio_ofcl_storms_shp.zip',
    # 'taos_swio_ofcl_storms_shp.zip.sha256': 'tc_swio_ofcl_storms_shp.zip.sha256'
})
