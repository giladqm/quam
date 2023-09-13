from typing import List
from dataclasses import dataclass

from quam_components.core import *


@dataclass
class BareQuamComponent(QuamComponent):
    pass


def test_base_quam_component_reference():
    quam_elem = BareQuamComponent()
    quam_elem.a = ":test"
    assert quam_elem._references == {"a": ":test"}


def test_subclass_quam_component_reference():
    @dataclass
    class QuamComponentTest(QuamComponent):
        ...

    quam_elem = QuamComponentTest()
    quam_elem.a = ":test"
    assert quam_elem._references == {"a": ":test"}


@dataclass
class QuamComponentTest(QuamComponent):
    int_val: int


def test_quam_component_reference_after_initialization():
    quam_elem = QuamComponentTest(int_val=42)

    quam_elem.int_val = ":test"
    assert quam_elem._references == {"int_val": ":test"}


def test_quam_component_reference_during_initialization():
    quam_elem = QuamComponentTest(int_val=":test")
    assert quam_elem._references == {"int_val": ":test"}


def test_basic_reference():
    @dataclass
    class QuamRootTest(QuamRoot):
        quam_elem1: QuamComponentTest
        quam_elem2: QuamComponentTest

    quam_elem1 = QuamComponentTest(int_val=1)
    quam_elem2 = QuamComponentTest(int_val=":quam_elem1.int_val")

    assert quam_elem1._references is not quam_elem2._references
    assert quam_elem2._references == {"int_val": ":quam_elem1.int_val"}

    quam = QuamRootTest(quam_elem1=quam_elem1, quam_elem2=quam_elem2)

    assert quam_elem1.int_val == 1
    assert quam_elem2.int_val == 1

    quam_elem2.int_val = ":quam_elem1"
    assert list(quam.iterate_components()) == [quam_elem1, quam_elem2]


def test_list_referencing():
    @dataclass
    class QuamRootTest(QuamRoot):
        quam_elems: List[QuamComponentTest]
        quam_elem2: QuamComponentTest

    quam_elems = [QuamComponentTest(int_val=k) for k in range(5)]
    quam_elem2 = QuamComponentTest(int_val=":quam_elems[3].int_val")

    assert quam_elem2._references == {"int_val": ":quam_elems[3].int_val"}

    quam = QuamRootTest(quam_elems=quam_elems, quam_elem2=quam_elem2)

    for k, elem in enumerate(quam.quam_elems):
        assert elem.int_val == k

    assert quam_elem2.int_val == 3


def test_reference_dict_elem():
    @dataclass
    class QuamRootTest(QuamRoot):
        quam_elem_dict: dict
        quam_elem2: QuamComponentTest

    quam_elem_dict = QuamDict(port_I=2)
    quam_elem2 = QuamComponentTest(int_val=":quam_elem_dict.port_I")

    assert quam_elem2._references == {"int_val": ":quam_elem_dict.port_I"}

    QuamRootTest(quam_elem_dict=quam_elem_dict, quam_elem2=quam_elem2)

    assert quam_elem2.int_val == 2


# TODO Test referencing when a quam element is added to a quam
