#!/usr/bin/env python3
"""
Simple example Python file for testing code suggestions.
This file contains basic Python constructs to test the suggester.
"""

import os
import sys
from typing import List, Dict


class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.history = []
        self.result = 0
    
    def add(self, value: float) -> float:
        """Add a value to the current result."""
        self.result += value
        self.history.append(f"add({value})")
        return self.result
    
    def subtract(self, value: float) -> float:
        """Subtract a value from the current result."""
        self.result -= value
        self.history.append(f"subtract({value})")
        return self.result
    
    def multiply(self, value: float) -> float:
        """Multiply the current result by a value."""
        self.result *= value
        self.history.append(f"multiply({value})")
        return self.result
    
    def divide(self, value: float) -> float:
        """Divide the current result by a value."""
        if value == 0:
            raise ValueError("Cannot divide by zero")
        self.result /= value
        self.history.append(f"divide({value})")
        return self.result
    
    def clear(self):
        """Clear the calculator."""
        self.result = 0
        self.history.clear()
    
    def get_history(self) -> List[str]:
        """Get the calculation history."""
        return self.history.copy()


def create_calculator() -> Calculator:
    """Factory function to create a new calculator."""
    return Calculator()


def main():
    """Main function to demonstrate calculator usage."""
    calc = create_calculator()
    
    # Perform some calculations
    calc.add(10)
    calc.multiply(2)
    calc.subtract(5)
    
    print(f"Result: {calc.result}")
    print(f"History: {calc.get_history()}")


if __name__ == "__main__":
    main()