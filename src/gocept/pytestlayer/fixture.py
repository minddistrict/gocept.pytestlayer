import contextlib
import pytest
import re
import time
import types
import zope.dottedname.resolve


class ZopeLayerState(object):

    def __init__(self):
        self.current = set()
        self.keep = set()
        self.keep_for_whole_session = set()


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
        reporter.write(f"{time_taken:.3f}", green=1, bold=1)
        reporter.write_line(" seconds.")


def setup_layer(layer, request):
    decorate_layer(layer, request)
    state = request.session.zopelayer_state
    layer_name = get_layer_name(layer)
    if hasattr(layer, 'setUp'):
        print(layer_name)
        with timer(request, f"Set up {layer_name} in "):
            layer.setUp()
        state.current.add(layer)


def teardown_layer(layer, request):
    decorate_layer(layer, request)
    state = request.session.zopelayer_state
    layer_name = get_layer_name(layer)
    if hasattr(layer, 'tearDown'):
        with timer(request, f"Tear down {layer_name} in "):
            layer.tearDown()
        state.current.remove(layer)


def session_fixture(request, layer):
    state = request.session.zopelayer_state
    if layer not in state.current:
        setup_layer(layer, request)
        state.keep_for_whole_session.add(layer)

    def teardown():
        teardown_layer(layer, request)
    request.addfinalizer(teardown)
    return layer


def class_fixture(request, layer):
    state = request.session.zopelayer_state
    if layer not in state.current:
        setup_layer(layer, request)

    def maybe_teardown():
        if layer not in (state.keep | state.keep_for_whole_session):
            teardown_layer(layer, request)
    request.addfinalizer(maybe_teardown)
    return layer


def function_fixture(request, layer):
    decorate_layer(layer, request)
    if hasattr(layer, 'testSetUp'):
        layer.testSetUp()

    if hasattr(layer, 'testTearDown'):

        def function_tear_down():
            decorate_layer(layer, request)
            layer.testTearDown()

        request.addfinalizer(function_tear_down)
    return layer


def decorate_layer(layer, request):
    setattr(layer, 'pytest_request', request)


def get_layer_name(layer):
    module = zope.dottedname.resolve.resolve(layer.__module__)
    for key, value in module.__dict__.items():
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
    return re.sub(r'\W|^(?=\d)', '_', string)


def get_fixture_name(layer, scope):
    name = make_identifier(get_layer_name(layer))
    layerid = id(layer)
    return 'zope_layer_{scope}_{name}_{layerid}'.format(**locals())


LAYERS = {}
LAYERS[object] = {}  # We do not need to create a fixture for `object`


def create(*layers, **kw):
    """Create fixtures for given layers and their bases.

    Fixture names will be generated automatically. For a single layer, you can
    pass in kw arguments ``session_fixture_name, ``class_fixture_name`` and
    ``function_fixture_name`` instead.

    """
    if kw and len(layers) > 1:
        raise ValueError(
            'Overriding layer names is only possible '
            'for a single layer at a time')

    ns = {}
    for layer in layers:
        if isinstance(layer, str):
            layer = zope.dottedname.resolve.resolve(layer)
        ns.update(_create_single(layer, **kw))
    return ns


SCOPES = ('session', 'class', 'function')
TEMPLATE = """\
@pytest.fixture(scope='session')
def {session_fixture_name}(request{session_fixture_dependencies}):
    "Depends on {session_fixture_dependencies}"
    return session_fixture(request, layer)

@pytest.fixture(scope='class')
def {class_fixture_name}(request{class_fixture_dependencies}):
    "Depends on {class_fixture_dependencies}"
    return class_fixture(request, layer)

@pytest.fixture(scope='function')
def {function_fixture_name}(request{function_fixture_dependencies}):
    "Depends on {function_fixture_dependencies}"
    return function_fixture(request, layer)
"""


def _create_single(layer, **kw):
    """Actually create a fixtures for a single layer and its bases."""
    if layer in LAYERS:
        return {}

    LAYERS[layer] = {}
    dependencies = {}
    for scope in SCOPES:
        LAYERS[layer][scope] = kw.get(
            '%s_fixture_name' % scope, get_fixture_name(layer, scope))
        dependencies[scope] = [
            ', ' + LAYERS.get(base, {}).get(
                scope, get_fixture_name(base, scope))
            for base in layer.__bases__ if base is not object]
    dependencies['function'].insert(0, ', ' + LAYERS[layer]['class'])

    fixtures = {}
    for scope in SCOPES:
        fixtures['%s_fixture_name' % scope] = LAYERS[layer][scope]
        fixtures['%s_fixture_dependencies' % scope] = ''.join(
            dependencies[scope])
    code = TEMPLATE.format(**fixtures)

    globs = {
        'pytest': pytest,
        'layer': layer,
    }
    for scope in SCOPES:
        globs['%s_fixture' % scope] = globals()['%s_fixture' % scope]

    ns = {}
    exec(code, globs, ns)

    # Recurse into bases:
    ns.update(create(*layer.__bases__))

    return ns


def parsefactories(collector, layer):
    ns = create(layer)
    if ns:
        name = get_fixture_name(layer, scope='function')
        module = types.ModuleType(name)
        module.__dict__.update(ns)
        collector.session._fixturemanager.parsefactories(module, '')


def raise_if_bad_layer(layer):
    'complaining about bad layers'

    if not hasattr(layer, '__bases__'):
        raise RuntimeError(
            "The layer {layer!r} has no __bases__ attribute."
            " Layers may be of two sorts: class or instance with __bases__"
            " attribute."
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
