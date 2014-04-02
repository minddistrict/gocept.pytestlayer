import contextlib
import pytest
import re
import time
import imp
import zope.dottedname.resolve


class ZopeLayerState(object):

    def __init__(self):
        self.current = set()
        self.keep = set()


@contextlib.contextmanager
def timer(request, text):
    verbose = request.config.option.verbose > 0
    reporter = request.config.pluginmanager.getplugin('terminalreporter')
    if verbose:
        reporter.ensure_newline()
        reporter.write(text)
        start = time.time()
    yield
    if verbose:
        time_taken = time.time() - start
        reporter.write("{0:.3f}".format(time_taken), green=1, bold=1)
        reporter.write_line(" seconds.")


def class_fixture(request, layer):
    decorate_layer(layer, request)
    state = request.session.zopelayer_state
    layer_name = get_layer_name(layer)

    if layer not in state.current:
        if hasattr(layer, 'setUp'):
            print layer_name
            with timer(request, "Set up {0} in ".format(layer_name)):
                layer.setUp()
            state.current.add(layer)

    def conditional_teardown():
        if layer not in state.keep:
            decorate_layer(layer, request)
            if hasattr(layer, 'tearDown'):
                with timer(request, "Tear down {0} in ".format(layer_name)):
                    layer.tearDown()
                state.current.remove(layer)

    request.addfinalizer(conditional_teardown)


def decorate_layer(layer, request):
    setattr(layer, 'pytest_request', request)


def function_fixture(request, layer):
    decorate_layer(layer, request)
    if hasattr(layer, 'testSetUp'):
        layer.testSetUp()

    if hasattr(layer, 'testTearDown'):

        def function_tear_down():
            decorate_layer(layer, request)
            layer.testTearDown()

        request.addfinalizer(function_tear_down)


def get_layer_name(layer):
    module = zope.dottedname.resolve.resolve(layer.__module__)
    for key, value in module.__dict__.iteritems():
        if value is layer:
            name = key
            break
    else:
        # As per zope.testrunner conventions, a layer is assumed to have a
        # __name__ even if it's not a class.
        name = layer.__name__
    return '%s.%s' % (layer.__module__, name)


def make_identifier(string):
    # Replaces things between words into underscores:
    return re.sub('\W|^(?=\d)', '_', string)


def get_fixture_name(layer, scope):
    name = make_identifier(get_layer_name(layer))
    layerid = id(layer)
    return 'zope_layer_{scope}_{name}_{layerid}'.format(**locals())


LAYERS = {}
LAYERS[object] = {}  # We do not need to create a fixture for `object`


def create(*layers, **kw):
    """Create fixtures for given layers and their bases.

    Fixture names will be generated automatically. For a single layer, you can
    pass in kw arguments ``class_fixture_name`` and ``function_fixture_name``
    instead.
    """
    if kw and len(layers > 1):
        raise ValueError(
            'Overriding layer names is only possible '
            'for a single layer at a time')

    ns = {}
    for layer in layers:
        if isinstance(layer, basestring):
            layer = zope.dottedname.resolve.resolve(layer)
        ns.update(_create_single(layer, **kw))
    return ns


TEMPLATE = """\
@pytest.fixture(scope='class')
def {class_fixture_name}(request{class_fixture_dependencies}):
    "Depends on {class_fixture_dependencies}"
    class_fixture(request, layer)

@pytest.fixture(scope='function')
def {function_fixture_name}(request{function_fixture_dependencies}):
    "Depends on {function_fixture_dependencies}"
    function_fixture(request, layer)
"""


def _create_single(layer, **kw):
    """Actually create a fixtures for a single layer and its bases."""
    if layer in LAYERS:
        return {}

    LAYERS[layer] = {}
    dependencies = {}
    for scope in ['class', 'function']:
        LAYERS[layer][scope] = kw.get(
            '%s_fixture_name' % scope, get_fixture_name(layer, scope))
        dependencies[scope] = [
            ', ' + LAYERS.get(base, {}).get(
                scope, get_fixture_name(base, scope))
            for base in layer.__bases__ if base is not object]
    dependencies['function'].insert(0, ', ' + LAYERS[layer]['class'])

    fixtures = {}
    for scope in ['class', 'function']:
        fixtures['%s_fixture_name' % scope] = LAYERS[layer][scope]
        fixtures['%s_fixture_dependencies' % scope] = ''.join(
            dependencies[scope])
    code = TEMPLATE.format(**fixtures)

    globs = dict(
        pytest=pytest,
        class_fixture=class_fixture,
        function_fixture=function_fixture,
        layer=layer,
    )
    ns = {}
    exec code in globs, ns

    # Recurse into bases:
    ns.update(create(*layer.__bases__))

    return ns


def parsefactories(collector, layer):
    ns = create(layer)
    if ns:
        name = get_fixture_name(layer, scope='function')
        module = imp.new_module(name)
        module.__dict__.update(ns)
        collector.session._fixturemanager.parsefactories(module, '')


def raise_if_bad_layer(layer):
    'complaining about bad layers'

    if not hasattr(layer, '__bases__'):
        raise RuntimeError(
            "The layer {0} has no __bases__ attribute."
            " Layers may be of two sorts: class or instance with __bases__"
            " attribute.".format(repr(layer))
        )


KEYWORDS_BY_LAYER = {object: {}}


def get_keywords(layer):
    if layer in KEYWORDS_BY_LAYER:
        return KEYWORDS_BY_LAYER[layer]
    keywords = {get_layer_name(layer): True}
    for base_layer in layer.__bases__:
        keywords.update(get_keywords(base_layer))
    KEYWORDS_BY_LAYER[layer] = keywords
    return keywords
