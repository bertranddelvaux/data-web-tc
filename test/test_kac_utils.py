import unittest
from scripts.kac_utils import mappingKAC

# ANSI color codes for printing - kept from your original code
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_PURPLE = "\033[35m"
ANSI_YELLOW = "\033[93m"
ANSI_ORANGE = "\033[38;5;202m"
ANSI_BOLD = "\033[1m"


class TestMappingKAC(unittest.TestCase):
    """
    Unit tests for the mappingKAC utility, including original printing messages.
    """

    def setUp(self):
        """
        Set up the mappingKAC instance for each test.
        """
        self.mapper = mappingKAC

    def _print_and_assert_mapping(self, url, url_backward, title=''):
        """
        Internal helper to perform printing and assertions for a single mapping pair.
        This method will be called by individual test cases.
        """
        print(f'\n\n\t{title}')

        # Test forward mapping
        print(f'\tForward Test:')
        print(f'\t  Input: {url}')
        forward_result = self.mapper.get_forward(url)
        print(f'\t  Output: {forward_result}')
        print(f'\t  Expected: {url_backward}')

        try:
            self.assertEqual(forward_result, url_backward, f"Forward mapping failed for {url}")
            print('\t✅ Forward mapping correct')
        except AssertionError as e:
            print('\t❌ Forward mapping incorrect')
            raise e  # Re-raise the exception so unittest marks the test as failed

        # Test backward mapping (if applicable)
        print(f'\tBackward Test:')
        print(f'\t  Input: {url_backward}')
        backward_result = self.mapper.get_backward(url_backward)
        print(f'\t  Output: {backward_result}')
        print(f'\t  Expected: {url}')

        try:
            self.assertEqual(backward_result, url, f"Backward mapping failed for {url_backward}")
            print('\t✅ Backward mapping correct')
        except AssertionError as e:
            print('\t❌ Backward mapping incorrect')
            raise e  # Re-raise the exception so unittest marks the test as failed

    def test_mpres_data_postevent_15as_nc(self):
        """
        Test case for mpres_data | postevent | 15as nc mapping.
        """
        title = f'mpres_data | postevent | 15as nc | {ANSI_PURPLE} <ATCFID>_<TECH>_SLOSH.nc {ANSI_RESET} -> {ANSI_ORANGE} tc_<ATCFID>_<TECH>.nc {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/ofcl_15as_nc/SH022025_JTWC_SLOSH.nc'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/postevent/tc_ofcl_15as_nc/tc_SH022025_JTWC.nc'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_mpres_data_postevent_30as_nc(self):
        """
        Test case for mpres_data | postevent | 30as nc mapping.
        """
        title = f'mpres_data | postevent | 30as nc | {ANSI_PURPLE} taostc_<ATCFID>_<TECH>_SLOSH.nc {ANSI_RESET} -> {ANSI_ORANGE} tc_<ATCFID>_<TECH>.nc {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/taos_swio30s_ofcl_windwater_nc/taostc_SH022025_JTWC_SLOSH.nc'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/postevent/tc_swio30s_ofcl_windwater_nc/tc_SH022025_JTWC.nc'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_mpres_data_postevent_30as_shp(self):
        """
        Test case for mpres_data | postevent | 30as shp mapping.
        """
        title = f'mpres_data | postevent | 30as shp | {ANSI_PURPLE} taos_swio30s_ofcl_windwater_shp_<ATCFID>.zip {ANSI_RESET} -> {ANSI_ORANGE} tc_swio30s_ofcl_windwater_shp_<ATCFID>.zip {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/taos_swio30s_ofcl_windwater_shp/taos_swio30s_ofcl_windwater_shp_SH072025.zip'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/postevent/tc_swio30s_ofcl_windwater_shp/tc_swio30s_ofcl_windwater_shp_SH072025.zip'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_mpres_data_taos_swio30s_ofcl_windwater_shp_zip(self):
        """
        Test case for mpres_data | taos_swio30s_ofcl_windwater_shp.zip mapping.
        """
        title = f'mpres_data | {ANSI_PURPLE} taos_swio30s_ofcl_windwater_shp.zip {ANSI_RESET} -> {ANSI_ORANGE} tc_swio30s_ofcl_windwater_shp.zip {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/taos_swio30s_ofcl_windwater_shp.zip'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/tc_swio30s_ofcl_windwater_shp.zip'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_mpres_data_taos_swio_ofcl_storms_shp_zip(self):
        """
        Test case for mpres_data | taos_swio_ofcl_storms_shp.zip mapping.
        """
        title = f'mpres_data | {ANSI_PURPLE} taos_swio_ofcl_storms_shp.zip {ANSI_RESET} -> {ANSI_ORANGE} tc_swio_ofcl_storms_shp.zip {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/taos_swio_ofcl_storms_shp.zip'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/tc_swio_ofcl_storms_shp.zip'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_mpres_data_daily_xsr_shp_zip(self):
        """
        Test case for mpres_data | daily_xsr_shp.zip mapping.
        """
        title = f'mpres_data | {ANSI_PURPLE} daily_xsr_shp.zip {ANSI_RESET} -> {ANSI_ORANGE} xr_daily_shp.zip {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/daily_xsr_shp.zip'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/xr_daily_shp.zip'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_tc_realtime_slosh_nc(self):
        """
        Test case for tc_realtime | taostc_<ATCFID>_<TECH>_SLOSH.nc mapping.
        """
        title = f'tc_realtime | {ANSI_PURPLE} taostc_<ATCFID>_<TECH>_SLOSH.nc {ANSI_RESET} -> {ANSI_ORANGE} tc_<ATCFID>_<TECH>.nc {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/tc_realtime/taostc_SH272025_JTWC_SLOSH.nc'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/tc_realtime/tc_SH272025_JTWC.nc'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_use_case_fetch_post_event_base_url(self):
        """
        Test case for Use Case | fetchPostEvent base URL mapping.
        """
        title = f'Use Case | {ANSI_PURPLE} https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/ {ANSI_RESET} -> {ANSI_ORANGE} https://kac.kacportal.com/portal/data/arc/postevent/ {ANSI_RESET}'
        url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/'
        url_backward = 'https://kac.kacportal.com/portal/data/arc/postevent/'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_use_case_ofcl_15as_nc(self):
        """
        Test case for Use Case | 'ofcl_15as_nc' mapping.
        """
        url = 'ofcl_15as_nc'
        url_backward = 'tc_ofcl_15as_nc'
        title = f'Use Case | {ANSI_PURPLE} {url} {ANSI_RESET} -> {ANSI_ORANGE} {url_backward} {ANSI_RESET}'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_use_case_taos_swio30s_ofcl_windwater_nc(self):
        """
        Test case for Use Case | 'taos_swio30s_ofcl_windwater_nc' mapping.
        """
        url = 'taos_swio30s_ofcl_windwater_nc'
        url_backward = 'tc_swio30s_ofcl_windwater_nc'
        title = f'Use Case | {ANSI_PURPLE} {url} {ANSI_RESET} -> {ANSI_ORANGE} {url_backward} {ANSI_RESET}'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_use_case_taos_swio30s_ofcl_windwater_shp(self):
        """
        Test case for Use Case | 'taos_swio30s_ofcl_windwater_shp' mapping.
        """
        url = 'taos_swio30s_ofcl_windwater_shp'
        url_backward = 'tc_swio30s_ofcl_windwater_shp'
        title = f'Use Case | {ANSI_PURPLE} {url} {ANSI_RESET} -> {ANSI_ORANGE} {url_backward} {ANSI_RESET}'
        self._print_and_assert_mapping(url, url_backward, title=title)

    def test_use_case_list_of_urls(self):
        """
        Test case for Use Case | List of URLs mapping.
        This case specifically tests mapping of lists, and assumes mappingKAC
        handles lists for forward mapping. Backward mapping for lists is not
        explicitly handled in your original comparison, so we'll only do forward.
        """
        urls = ['ofcl_15as_nc', 'taos_swio30s_ofcl_windwater_nc', 'taos_swio30s_ofcl_windwater_shp']
        expected_backward_urls = ['tc_ofcl_15as_nc', 'tc_swio30s_ofcl_windwater_nc', 'tc_swio30s_ofcl_windwater_shp']
        title = f'Use Case | {ANSI_PURPLE} {urls} {ANSI_RESET} -> {ANSI_ORANGE} {expected_backward_urls} {ANSI_RESET}'

        print(f'\n\n\t{title}')
        print(f'\tForward Test (List):')
        print(f'\t  Input: {urls}')
        forward_result = self.mapper.get_forward(urls)
        print(f'\t  Output: {forward_result}')
        print(f'\t  Expected: {expected_backward_urls}')

        try:
            self.assertEqual(forward_result, expected_backward_urls, "Forward mapping failed for list of URLs")
            print('\t✅ Forward mapping correct')
        except AssertionError as e:
            print('\t❌ Forward mapping incorrect')
            raise e  # Re-raise the exception so unittest marks the test as failed

        # Note: The original code did not perform backward mapping check for lists,
        # so we're not including it here to maintain fidelity with your original intent.
        # If mappingKAC.get_backward is expected to handle lists, you would add that here.


if __name__ == '__main__':
    # Add a print statement to indicate the start of tests
    print(f"{ANSI_BOLD}Starting mappingKAC tests with detailed output...{ANSI_RESET}")
    # We set verbosity to 0 or 1 to minimize unittest's own output,
    # relying more on our custom prints. Verbosity 2 is more detailed from unittest.
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=1)
