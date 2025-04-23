from dataclasses import dataclass
from behave import then, given, when


@dataclass
class ContextType:
    input_some_attr: str


@given("input some_attr `{some_attr}` provided")
def add_some_attr(context: ContextType, some_attr: str) -> None:
    context.input_some_attr = some_attr


@when("some request is made")
def run_some_request(context: ContextType) -> None:
    pass


@then("somthing happens")
def check_something(context: ContextType) -> None:
    pass
