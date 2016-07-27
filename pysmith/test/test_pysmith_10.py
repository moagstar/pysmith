import mock
import pysmith.pysmith_10


def test_one_of_const():

    def draw(x):
        return x.example()

    assert pysmith.pysmith_10._one_of_const(draw, '') == ''
    assert pysmith.pysmith_10._one_of_const(draw, 'a') == 'a'
    # TODO : test optional with 1 const
    # TODO : multiple consts
    # TODO : multiple consts with optional


def test_expr_builder():

    assert not pysmith.pysmith_10.factor().example()
