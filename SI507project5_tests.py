import unittest
from SI507project5_code import *

class Project5(unittest.TestCase):
    def setUp(self):
        self.tumblr_test = get_data_from_api("chunkyknit")
        self.tumblr_instance = Tumblr(self.tumblr_test)
        self.tumblr_post = get_data_from_api("chunkyknit", "posts")

    def test_cache(self):
        testfile = open(CACHE_FNAME,'r')
        tfstr = testfile.read()
        testfile.close()
        self.assertTrue(len(tfstr) != 0, "Testing that there is data in the cache.")

    def test_cache_two(self):
        testfile = open(CACHE_FNAME, 'r')
        tfstr = testfile.read()
        testfile.close()
        self.assertTrue("chunkyknit" in tfstr, "Testing that the Tumblr API data has been correctly cached.")

    def test_creds_cache(self):
        testfile = open(CREDS_CACHE_FILE, 'r')
        tfstr = testfile.read()
        testfile.close()
        self.assertTrue(len(tfstr) != 0, "Testing that there is data in the creds cache.")

    def test_tumblr_api(self):
        self.assertTrue(type(self.tumblr_test) == type({}), "Testing that the Tumblr API returns a dictionary.")
        self.assertEqual(len(self.tumblr_test.keys()), 2, "Testing that the dictionary is not empty.")

    def test_class_tumblr(self):
        self.assertTrue(self.tumblr_instance.title == "", "Testing that Class Tumblr correctly returns data.")

    def test_class_tum_posts(self):
        for tum in range(len(self.tumblr_post["response"]["posts"])):
            tum_post = Tumblr_Posts(self.tumblr_post["response"]["posts"][tum])
        self.assertTrue(tum_post.blog == "chunkyknit", "Testing that Class Tumblr_Posts returns the data I intend it to.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
