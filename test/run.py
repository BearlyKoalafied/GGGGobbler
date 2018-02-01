import unittest



def run():
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    runner = unittest.TextTestRunner()
    runner.run(tests)

if __name__ == '__main__':
    run()
