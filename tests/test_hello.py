from TwitterClone.hello import hello

def test_ci_pipeline_codecov():
    assert True

def test_hello():
    assert hello() == "Hello, World!"