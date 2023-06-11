def assert_equals(func, result):
    print("-" * 40)
    print("Test:", func)
    print("Expected:", result)
    print("Comparison:", func == result)
    print("-" * 40)


def expect(compa, error):
    print("-" * 40)
    print("Comparison:", compa)
    if not compa:
        print("Error:", error)
    print("-" * 40)
