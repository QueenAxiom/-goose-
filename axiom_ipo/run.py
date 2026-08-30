#!/usr/bin/env python3
"""
Axiom IPO Intelligence - Run Script
Starts the Flask web application
"""

from axiom_ipo.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("Axiom IPO Intelligence Prototype")
    print("=" * 60)
    print()
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()
    app.run(debug=True, port=5000)
