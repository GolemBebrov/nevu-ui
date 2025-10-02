import pytest
import nevu_ui as ui
import pygame

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()

@pytest.fixture
def elements():
    return [
        ui.widgets.element_switcher.Element("Apple", "fruit_1"),
        ui.widgets.element_switcher.Element("Banana", "fruit_2"),
        ui.widgets.element_switcher.Element("Cherry", "fruit_3"),
        ui.widgets.element_switcher.Element("Date", "fruit_4"),
        ui.widgets.element_switcher.Element("Banana", "fruit_5")
    ]

@pytest.fixture
def switcher(elements):
    switcher_instance = ui.widgets.ElementSwitcher(size=[200, 50], elements=elements)
    switcher_instance._lazy_init(size=[200, 50], elements=elements)
    return switcher_instance

class TestElementSwitcherArrayInteraction:

    def test_initial_count(self, switcher):
        assert switcher.count() == 5

    def test_add_element(self, switcher):
        initial_count = switcher.count()
        new_element = ui.widgets.element_switcher.Element("Fig", "fruit_6")
        switcher.add_element(new_element)
        assert switcher.count() == initial_count + 1
        assert switcher.elements[-1].id == "fruit_6"

    def test_find(self, switcher):
        found_element = switcher.find("fruit_3")
        assert found_element is not None
        assert found_element.text == "Cherry"

    def test_find_nonexistent(self, switcher):
        found_element = switcher.find("fruit_99")
        assert found_element is None

    def test_rfind(self, switcher):
        found_element = switcher.rfind("fruit_2")
        assert found_element is not None
        assert found_element.text == "Banana"

    def test_remove(self, switcher):
        initial_count = switcher.count()
        switcher.remove("fruit_3")
        assert switcher.count() == initial_count - 1
        assert switcher.find("fruit_3") is None

    def test_remove_nonexistent_raises_error(self, switcher):
        with pytest.raises(ValueError):
            switcher.remove("fruit_99")

    def test_move_to(self, switcher):
        assert switcher.current_index == 0
        switcher.move_to("fruit_4")
        assert switcher.current_index == 3
        assert switcher.current_element.text == "Date"

    def test_move_to_nonexistent_raises_error(self, switcher):
        with pytest.raises(ValueError):
            switcher.move_to("fruit_99")

    def test_elements_create_helper(self):
        elements_list = ui.widgets.element_switcher.Elements.create(
            "Text1",
            ["Text2", "id2"],
            ("Text3", "id3"),
            ui.widgets.element_switcher.Element("Text4", "id4")
        )
        assert len(elements_list) == 4
        assert elements_list[0].text == "Text4" and elements_list[0].id == "id4"
        assert elements_list[1].text == "Text1" and elements_list[1].id is None
        assert elements_list[2].text == "Text2" and elements_list[2].id == "id2"
        assert elements_list[3].text == "Text3" and elements_list[3].id == "id3"