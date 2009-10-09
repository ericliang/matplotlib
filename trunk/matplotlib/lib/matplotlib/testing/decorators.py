from matplotlib.testing.noseclasses import KnownFailureTest, \
     KnownFailureDidNotFailTest, ImageComparisonFailure
import os, sys
import nose
import matplotlib
import matplotlib.tests
from matplotlib.testing.compare import comparable_formats, compare_images

def knownfailureif(fail_condition, msg=None):
    """

    Assume a will fail if *fail_condition* is True. *fail_condition*
    may also be False or the string 'indeterminate'.

    *msg* is the error message displayed for the test.

    """
    # based on numpy.testing.dec.knownfailureif
    if msg is None:
        msg = 'Test known to fail'
    def known_fail_decorator(f):
        # Local import to avoid a hard nose dependency and only incur the
        # import time overhead at actual test-time.
        import nose
        def failer(*args, **kwargs):
            try:
                # Always run the test (to generate images).
                result = f(*args, **kwargs)
            except:
                if fail_condition:
                    # (Keep the next ultra-long comment so in shows in console.)
                    raise KnownFailureTest(msg) # An error here when running nose means that you don't have the matplotlib.testing.noseclasses:KnownFailure plugin in use.
                else:
                    raise
            if fail_condition and fail_condition != 'indeterminate':
                raise KnownFailureDidNotFailTest(msg)
            return result
        return nose.tools.make_decorator(f)(failer)
    return known_fail_decorator

def image_comparison(baseline_images=None):
    """
    compare images generated by the test with those specified in
    *baseline_images*, which must correspond else an
    ImageComparisonFailure exception will be raised.
    """

    if baseline_images is None:
        raise ValueError('baseline_images must be specified')

    # The multiple layers of defs are required because of how
    # parameterized decorators work, and because we want to turn the
    # single test_foo function to a generator that generates a
    # separate test case for each file format.
    def compare_images_decorator(func):
        baseline_dir, result_dir = _image_directories(func)
        extensions = ['png', 'pdf']

        def compare_images_generator():
            for extension in extensions:
                @knownfailureif(extension not in comparable_formats(),
                                'Cannot compare %s files on this system' % extension)
                def decorated_compare_images():
                    # set the default format of savefig
                    matplotlib.rc('savefig', extension=extension)
                    # change to the result directory for the duration of the test
                    old_dir = os.getcwd()
                    os.chdir(result_dir)
                    try:
                        result = func() # actually call the test function
                    finally:
                        os.chdir(old_dir)
                    for fname in baseline_images:
                        actual = os.path.join(result_dir, fname) + '.' + extension
                        expected = os.path.join(baseline_dir,fname) + '.' + extension

                        # compare the images
                        tol=1e-3 # default tolerance
                        err = compare_images( expected, actual, tol,
                                              in_decorator=True )
                        if err:
                            raise ImageComparisonFailure(
                                'images not close: %(actual)s vs. %(expected)s '
                                '(RMS %(rms).3f)'%err)
                    return result
                yield (decorated_compare_images,)
        return nose.tools.make_decorator(func)(compare_images_generator)
    return compare_images_decorator

def _image_directories(func):
    """
    Compute the baseline and result image directories for testing *func*.
    Create the result directory if it doesn't exist.
    """
    module_name = func.__module__
    if module_name=='__main__':
        # FIXME: this won't work for nested packages in matplotlib.tests
        import warnings
        warnings.warn('test module run as script. guessing baseline image locations')
        script_name = sys.argv[0]
        basedir = os.path.abspath(os.path.dirname(script_name))
        subdir = os.path.splitext(os.path.split(script_name)[1])[0]
    else:
        mods = module_name.split('.')
        assert mods.pop(0)=='matplotlib'
        assert mods.pop(0)=='tests'
        subdir = os.path.join(*mods)
        basedir = os.path.dirname(matplotlib.tests.__file__)

    baseline_dir = os.path.join(basedir,'baseline_images',subdir)
    result_dir = os.path.join(basedir,'current_images',subdir)

    if not os.path.exists(result_dir):
        try:
            # make the current_images directory first
            os.mkdir(os.path.join(basedir,'current_images'))
        except OSError:
            pass # probably exists already
        os.mkdir(result_dir)

    return baseline_dir, result_dir

